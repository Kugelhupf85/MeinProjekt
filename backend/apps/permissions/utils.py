"""
Permission Utilities for Arcanovi.
Provides helper functions for permission hierarchy and inheritance.
"""
from typing import List, Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone

from .models.permission import Permission

User = get_user_model()


def check_permission_hierarchy(permission_type: str, required_permission: str) -> bool:
    """
    Check if a permission type includes the required permission level.
    
    Permission hierarchy: admin > delete > edit > view
    
    Args:
        permission_type: The permission type to check
        required_permission: The required permission level
        
    Returns:
        bool: True if permission_type includes required_permission
    """
    hierarchy = {
        'view': 1,
        'edit': 2,
        'delete': 3,
        'admin': 4,
    }
    
    return hierarchy.get(permission_type, 0) >= hierarchy.get(required_permission, 0)


def has_permission(user, resource, permission_type: str) -> bool:
    """
    Check if user has a specific permission on a resource.
    Includes hierarchy checking and inheritance logic.
    
    Args:
        user: User instance
        resource: Resource instance
        permission_type: Required permission type
        
    Returns:
        bool: True if user has permission
    """
    if user is None or not user.is_authenticated:
        return False
    
    # Check direct permissions
    if Permission.has_permission(user, resource, permission_type):
        return True
    
    # Check for higher-level permissions
    for higher_permission in ['admin', 'delete', 'edit']:
        if higher_permission != permission_type:
            if Permission.has_permission(user, resource, higher_permission):
                if check_permission_hierarchy(higher_permission, permission_type):
                    return True
    
    return False


def get_user_permissions(user, resource_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all permissions for a user, formatted for frontend.
    
    Args:
        user: User instance
        resource_type: Optional resource type filter
        
    Returns:
        List of permission dictionaries
    """
    permissions = Permission.get_user_permissions(user, resource_type)
    
    result = []
    for permission in permissions:
        result.append({
            'id': permission.id,
            'permission_type': permission.permission_type,
            'resource_type': permission.resource_type,
            'resource_id': permission.object_id,
            'resource_name': str(permission.resource) if permission.resource else 'Unknown',
            'granted_at': permission.granted_at.isoformat(),
            'granted_by': permission.granted_by.email if permission.granted_by else None,
            'expires_at': permission.expires_at.isoformat() if permission.expires_at else None,
            'is_valid': permission.is_valid(),
            'notes': permission.notes,
        })
    
    return result


def get_accessible_resources(user, resource_type: str, permission_type: str = 'view') -> List[int]:
    """
    Get list of resource IDs that a user can access with the given permission.
    
    Args:
        user: User instance
        resource_type: Type of resources to check
        permission_type: Minimum permission level required
        
    Returns:
        List of resource IDs
    """
    if not user.is_authenticated:
        return []
    
    # Get all permissions for this user and resource type
    permissions = Permission.objects.filter(
        user=user,
        resource_type=resource_type,
        is_active=True
    ).select_related('content_type')
    
    accessible_ids = set()
    
    for permission in permissions:
        if not permission.is_valid():
            continue
        
        # Check if this permission includes the required level
        if check_permission_hierarchy(permission.permission_type, permission_type):
            accessible_ids.add(permission.object_id)
    
    return list(accessible_ids)


def grant_permission_inheritance(user, parent_resource, child_resource, permission_type: str, granted_by=None):
    """
    Grant permission on child resource based on parent resource permission.
    Used for World → Adventure inheritance.
    
    Args:
        user: User instance
        parent_resource: Parent resource (e.g., World)
        child_resource: Child resource (e.g., Adventure)
        permission_type: Permission type to grant
        granted_by: User granting the permission
        
    Returns:
        Permission instance or None
    """
    # Check if user has permission on parent resource
    if not has_permission(user, parent_resource, permission_type):
        return None
    
    # Grant permission on child resource
    return Permission.grant_permission(
        user=user,
        resource=child_resource,
        permission_type=permission_type,
        granted_by=granted_by,
        notes=f"Inherited from {parent_resource.__class__.__name__} {parent_resource.id}"
    )


def bulk_grant_permissions(users: List[User], resource, permission_type: str, granted_by=None, expires_at=None):
    """
    Grant permissions to multiple users at once.
    
    Args:
        users: List of User instances
        resource: Resource instance
        permission_type: Permission type to grant
        granted_by: User granting the permissions
        expires_at: Optional expiration date
        
    Returns:
        List of created Permission instances
    """
    permissions = []
    
    for user in users:
        permission = Permission.grant_permission(
            user=user,
            resource=resource,
            permission_type=permission_type,
            granted_by=granted_by,
            expires_at=expires_at
        )
        permissions.append(permission)
    
    return permissions


def revoke_all_permissions(user, resource):
    """
    Revoke all permissions for a user on a specific resource.
    
    Args:
        user: User instance
        resource: Resource instance
        
    Returns:
        int: Number of permissions revoked
    """
    content_type = ContentType.objects.get_for_model(resource)
    
    permissions = Permission.objects.filter(
        user=user,
        content_type=content_type,
        object_id=resource.id,
        is_active=True
    )
    
    count = permissions.count()
    permissions.update(is_active=False)
    
    return count


def cleanup_expired_permissions():
    """
    Clean up expired permissions by setting them to inactive.
    
    Returns:
        int: Number of permissions cleaned up
    """
    now = timezone.now()
    
    expired_permissions = Permission.objects.filter(
        expires_at__lt=now,
        is_active=True
    )
    
    count = expired_permissions.count()
    expired_permissions.update(is_active=False)
    
    return count


def get_permission_summary(user, resource_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a summary of user's permissions.
    
    Args:
        user: User instance
        resource_type: Optional resource type filter
        
    Returns:
        Dictionary with permission summary
    """
    permissions = Permission.get_user_permissions(user, resource_type)
    
    summary = {
        'total_permissions': len(permissions),
        'by_resource_type': {},
        'by_permission_type': {},
        'recent_permissions': [],
        'expiring_soon': [],
    }
    
    for permission in permissions:
        # Count by resource type
        resource_type = permission.resource_type
        if resource_type not in summary['by_resource_type']:
            summary['by_resource_type'][resource_type] = 0
        summary['by_resource_type'][resource_type] += 1
        
        # Count by permission type
        perm_type = permission.permission_type
        if perm_type not in summary['by_permission_type']:
            summary['by_permission_type'][perm_type] = 0
        summary['by_permission_type'][perm_type] += 1
        
        # Recent permissions (last 30 days)
        if permission.granted_at >= timezone.now() - timezone.timedelta(days=30):
            summary['recent_permissions'].append({
                'id': permission.id,
                'resource_type': permission.resource_type,
                'permission_type': permission.permission_type,
                'granted_at': permission.granted_at.isoformat(),
            })
        
        # Expiring soon (next 7 days)
        if permission.expires_at:
            if permission.expires_at <= timezone.now() + timezone.timedelta(days=7):
                summary['expiring_soon'].append({
                    'id': permission.id,
                    'resource_type': permission.resource_type,
                    'permission_type': permission.permission_type,
                    'expires_at': permission.expires_at.isoformat(),
                })
    
    return summary 