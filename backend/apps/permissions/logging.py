"""
Permission Logging for Arcanovi.
Tracks permission checks, changes, and failed attempts for audit purposes.
"""
import logging
from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db import models

from .models.permission import Permission

User = get_user_model()

# Configure logger
logger = logging.getLogger('permissions')


class PermissionLog(models.Model):
    """
    Model to log permission-related activities for audit purposes.
    """
    
    LOG_TYPES = [
        ('check', 'Permission Check'),
        ('grant', 'Permission Granted'),
        ('revoke', 'Permission Revoked'),
        ('failed', 'Failed Permission Attempt'),
        ('inheritance', 'Permission Inheritance'),
        ('bulk', 'Bulk Permission Operation'),
    ]
    
    # Log metadata
    log_type = models.CharField(
        max_length=20,
        choices=LOG_TYPES,
        help_text='Type of permission activity'
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text='When this log entry was created'
    )
    
    # User information
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='permission_logs',
        help_text='User involved in the permission activity'
    )
    
    # Resource information
    resource_type = models.CharField(
        max_length=20,
        help_text='Type of resource involved'
    )
    
    resource_id = models.PositiveIntegerField(
        help_text='ID of the resource involved'
    )
    
    # Permission information
    permission_type = models.CharField(
        max_length=20,
        help_text='Type of permission involved'
    )
    
    # Additional context
    success = models.BooleanField(
        default=True,
        help_text='Whether the permission operation was successful'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the request'
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text='User agent of the request'
    )
    
    request_path = models.CharField(
        max_length=500,
        blank=True,
        help_text='Request path that triggered the permission check'
    )
    
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about the permission activity'
    )
    
    # Related permission (if applicable)
    permission = models.ForeignKey(
        Permission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs',
        help_text='Related permission instance'
    )
    
    class Meta:
        db_table = 'permissions_log'
        verbose_name = 'Permission Log'
        verbose_name_plural = 'Permission Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['log_type', 'success']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_log_type_display()} - {self.user.email} on {self.resource_type} {self.resource_id}"


def log_permission_check(user, resource, permission_type: str, success: bool, request=None, notes: str = ''):
    """
    Log a permission check attempt.
    
    Args:
        user: User instance
        resource: Resource instance
        permission_type: Permission type being checked
        success: Whether the check was successful
        request: HTTP request object (optional)
        notes: Additional notes
    """
    try:
        log_entry = PermissionLog.objects.create(
            log_type='check',
            user=user,
            resource_type=Permission._get_resource_type(resource),
            resource_id=resource.id,
            permission_type=permission_type,
            success=success,
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else None,
            request_path=get_request_path(request) if request else None,
            notes=notes,
        )
        
        # Log to Django logger as well
        if success:
            logger.info(f"Permission check: {user.email} has {permission_type} on {resource}")
        else:
            logger.warning(f"Permission denied: {user.email} lacks {permission_type} on {resource}")
        
        return log_entry
    
    except Exception as e:
        logger.error(f"Failed to log permission check: {e}")


def log_permission_grant(user, resource, permission_type: str, granted_by=None, request=None, notes: str = ''):
    """
    Log a permission grant.
    
    Args:
        user: User receiving the permission
        resource: Resource instance
        permission_type: Permission type granted
        granted_by: User granting the permission
        request: HTTP request object (optional)
        notes: Additional notes
    """
    try:
        # Get the permission instance
        permission = Permission.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(resource),
            object_id=resource.id,
            permission_type=permission_type
        ).first()
        
        log_entry = PermissionLog.objects.create(
            log_type='grant',
            user=user,
            resource_type=Permission._get_resource_type(resource),
            resource_id=resource.id,
            permission_type=permission_type,
            success=True,
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else None,
            request_path=get_request_path(request) if request else None,
            notes=notes,
            permission=permission,
        )
        
        logger.info(f"Permission granted: {granted_by.email if granted_by else 'System'} granted {permission_type} to {user.email} on {resource}")
        
        return log_entry
    
    except Exception as e:
        logger.error(f"Failed to log permission grant: {e}")


def log_permission_revoke(user, resource, permission_type: str, revoked_by=None, request=None, notes: str = ''):
    """
    Log a permission revocation.
    
    Args:
        user: User losing the permission
        resource: Resource instance
        permission_type: Permission type revoked
        revoked_by: User revoking the permission
        request: HTTP request object (optional)
        notes: Additional notes
    """
    try:
        # Get the permission instance
        permission = Permission.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(resource),
            object_id=resource.id,
            permission_type=permission_type
        ).first()
        
        log_entry = PermissionLog.objects.create(
            log_type='revoke',
            user=user,
            resource_type=Permission._get_resource_type(resource),
            resource_id=resource.id,
            permission_type=permission_type,
            success=True,
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else None,
            request_path=get_request_path(request) if request else None,
            notes=notes,
            permission=permission,
        )
        
        logger.info(f"Permission revoked: {revoked_by.email if revoked_by else 'System'} revoked {permission_type} from {user.email} on {resource}")
        
        return log_entry
    
    except Exception as e:
        logger.error(f"Failed to log permission revoke: {e}")


def log_failed_permission_attempt(user, resource, permission_type: str, request=None, notes: str = ''):
    """
    Log a failed permission attempt.
    
    Args:
        user: User attempting the action
        resource: Resource instance
        permission_type: Permission type that was needed
        request: HTTP request object (optional)
        notes: Additional notes
    """
    try:
        log_entry = PermissionLog.objects.create(
            log_type='failed',
            user=user,
            resource_type=Permission._get_resource_type(resource),
            resource_id=resource.id,
            permission_type=permission_type,
            success=False,
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else None,
            request_path=get_request_path(request) if request else None,
            notes=notes,
        )
        
        logger.warning(f"Failed permission attempt: {user.email} attempted {permission_type} on {resource}")
        
        return log_entry
    
    except Exception as e:
        logger.error(f"Failed to log failed permission attempt: {e}")


def log_permission_inheritance(user, parent_resource, child_resource, permission_type: str, request=None, notes: str = ''):
    """
    Log permission inheritance.
    
    Args:
        user: User receiving inherited permission
        parent_resource: Parent resource
        child_resource: Child resource
        permission_type: Permission type inherited
        request: HTTP request object (optional)
        notes: Additional notes
    """
    try:
        log_entry = PermissionLog.objects.create(
            log_type='inheritance',
            user=user,
            resource_type=Permission._get_resource_type(child_resource),
            resource_id=child_resource.id,
            permission_type=permission_type,
            success=True,
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else None,
            request_path=get_request_path(request) if request else None,
            notes=f"Inherited from {parent_resource.__class__.__name__} {parent_resource.id}. {notes}",
        )
        
        logger.info(f"Permission inheritance: {user.email} inherited {permission_type} on {child_resource} from {parent_resource}")
        
        return log_entry
    
    except Exception as e:
        logger.error(f"Failed to log permission inheritance: {e}")


def log_bulk_permission_operation(users, resource, permission_type: str, operation: str, performed_by=None, request=None, notes: str = ''):
    """
    Log bulk permission operations.
    
    Args:
        users: List of User instances
        resource: Resource instance
        permission_type: Permission type involved
        operation: Type of operation (grant, revoke)
        performed_by: User performing the operation
        request: HTTP request object (optional)
        notes: Additional notes
    """
    try:
        log_entries = []
        
        for user in users:
            log_entry = PermissionLog.objects.create(
                log_type='bulk',
                user=user,
                resource_type=Permission._get_resource_type(resource),
                resource_id=resource.id,
                permission_type=permission_type,
                success=True,
                ip_address=get_client_ip(request) if request else None,
                user_agent=get_user_agent(request) if request else None,
                request_path=get_request_path(request) if request else None,
                notes=f"Bulk {operation} operation. {notes}",
            )
            log_entries.append(log_entry)
        
        logger.info(f"Bulk permission {operation}: {performed_by.email if performed_by else 'System'} {operation}ed {permission_type} for {len(users)} users on {resource}")
        
        return log_entries
    
    except Exception as e:
        logger.error(f"Failed to log bulk permission operation: {e}")


def get_permission_audit_trail(user, resource_type: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
    """
    Get permission audit trail for a user.
    
    Args:
        user: User instance
        resource_type: Optional resource type filter
        days: Number of days to look back
        
    Returns:
        Dictionary with audit trail information
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=days)
    
    queryset = PermissionLog.objects.filter(
        user=user,
        timestamp__gte=cutoff_date
    )
    
    if resource_type:
        queryset = queryset.filter(resource_type=resource_type)
    
    logs = queryset.order_by('-timestamp')
    
    summary = {
        'total_activities': logs.count(),
        'successful_activities': logs.filter(success=True).count(),
        'failed_attempts': logs.filter(success=False).count(),
        'by_log_type': {},
        'by_resource_type': {},
        'recent_activities': [],
    }
    
    # Count by log type
    for log_type, _ in PermissionLog.LOG_TYPES:
        count = logs.filter(log_type=log_type).count()
        if count > 0:
            summary['by_log_type'][log_type] = count
    
    # Count by resource type
    resource_types = logs.values_list('resource_type', flat=True).distinct()
    for resource_type in resource_types:
        count = logs.filter(resource_type=resource_type).count()
        summary['by_resource_type'][resource_type] = count
    
    # Recent activities (last 10)
    recent_logs = logs[:10]
    for log in recent_logs:
        summary['recent_activities'].append({
            'id': log.id,
            'log_type': log.log_type,
            'resource_type': log.resource_type,
            'resource_id': log.resource_id,
            'permission_type': log.permission_type,
            'success': log.success,
            'timestamp': log.timestamp.isoformat(),
            'notes': log.notes,
        })
    
    return summary


def cleanup_old_permission_logs(days: int = 90):
    """
    Clean up old permission logs.
    
    Args:
        days: Number of days to keep logs
        
    Returns:
        int: Number of logs deleted
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=days)
    
    old_logs = PermissionLog.objects.filter(timestamp__lt=cutoff_date)
    count = old_logs.count()
    
    old_logs.delete()
    
    logger.info(f"Cleaned up {count} old permission logs (older than {days} days)")
    
    return count


# Helper functions for extracting request information
def get_client_ip(request):
    """Extract client IP from request."""
    if not request:
        return None
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip


def get_user_agent(request):
    """Extract user agent from request."""
    if not request:
        return ''
    
    return request.META.get('HTTP_USER_AGENT', '')


def get_request_path(request):
    """Extract request path from request."""
    if not request:
        return ''
    
    return request.path 