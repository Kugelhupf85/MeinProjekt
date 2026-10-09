"""
Permission Model for Arcanovi.
Provides granular permission system for resources (world, adventure, character, rule_set).
"""
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Permission(models.Model):
    """
    Generic permission model for resources.
    Supports different resource types and permission levels.
    """
    
    PERMISSION_TYPES = [
        ('view', _('View')),
        ('edit', _('Edit')),
        ('delete', _('Delete')),
        ('admin', _('Admin')),
    ]
    
    RESOURCE_TYPES = [
        ('world', _('World')),
        ('adventure', _('Adventure')),
        ('character', _('Character')),
        ('rule_set', _('Rule Set')),
    ]
    
    # User who has the permission
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='permissions',
        help_text=_('The user who has this permission')
    )
    
    # Permission type
    permission_type = models.CharField(
        max_length=20,
        choices=PERMISSION_TYPES,
        help_text=_('Type of permission granted')
    )
    
    # Resource type (for filtering and validation)
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPES,
        help_text=_('Type of resource this permission applies to')
    )
    
    # Generic foreign key to the resource
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='arcanovi_permissions',
        help_text=_('Content type of the resource')
    )
    object_id = models.CharField(
        max_length=36,
        help_text=_('ID of the resource')
    )
    resource = GenericForeignKey('content_type', 'object_id')
    
    # Permission metadata
    granted_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When this permission was granted')
    )
    
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_permissions',
        help_text=_('User who granted this permission')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this permission is currently active')
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When this permission expires (optional)')
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_('Additional notes about this permission')
    )
    
    class Meta:
        db_table = 'permissions_permission'
        verbose_name = _('Permission')
        verbose_name_plural = _('Permissions')
        unique_together = ['user', 'content_type', 'object_id', 'permission_type']
        ordering = ['user', 'resource_type', 'permission_type']
        indexes = [
            models.Index(fields=['user', 'resource_type']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['permission_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_permission_type_display()} on {self.resource_type}"
    
    def is_expired(self):
        """Check if permission has expired."""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
    
    def is_valid(self):
        """Check if permission is currently valid."""
        return self.is_active and not self.is_expired()
    
    @classmethod
    def grant_permission(cls, user, resource, permission_type, granted_by=None, expires_at=None, notes=''):
        """
        Grant a permission to a user for a specific resource.
        
        Args:
            user: User instance
            resource: Resource instance (World, Adventure, etc.)
            permission_type: String permission type
            granted_by: User granting the permission
            expires_at: Optional expiration date
            notes: Optional notes
            
        Returns:
            Permission instance
        """
        content_type = ContentType.objects.get_for_model(resource)
        
        permission, created = cls.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=resource.id,
            permission_type=permission_type,
            defaults={
                'resource_type': cls._get_resource_type(resource),
                'granted_by': granted_by,
                'expires_at': expires_at,
                'notes': notes,
                'is_active': True,
            }
        )
        
        if not created:
            # Update existing permission
            permission.is_active = True
            permission.granted_by = granted_by
            permission.expires_at = expires_at
            permission.notes = notes
            permission.save()
        
        return permission
    
    @classmethod
    def revoke_permission(cls, user, resource, permission_type):
        """
        Revoke a permission from a user.
        
        Args:
            user: User instance
            resource: Resource instance
            permission_type: String permission type
            
        Returns:
            bool: True if permission was revoked, False if not found
        """
        content_type = ContentType.objects.get_for_model(resource)
        
        try:
            permission = cls.objects.get(
                user=user,
                content_type=content_type,
                object_id=resource.id,
                permission_type=permission_type
            )
            permission.is_active = False
            permission.save()
            return True
        except cls.DoesNotExist:
            return False
    
    @classmethod
    def has_permission(cls, user, resource, permission_type):
        """
        Check if user has a specific permission on a resource.
        
        Args:
            user: User instance
            resource: Resource instance
            permission_type: String permission type
            
        Returns:
            bool: True if user has permission
        """
        if not user.is_authenticated:
            return False
        
        content_type = ContentType.objects.get_for_model(resource)
        
        # Check for exact permission
        exact_permission = cls.objects.filter(
            user=user,
            content_type=content_type,
            object_id=resource.id,
            permission_type=permission_type,
            is_active=True
        ).first()
        
        if exact_permission and exact_permission.is_valid():
            return True
        
        # Check for higher-level permission (admin includes all)
        if permission_type != 'admin':
            admin_permission = cls.objects.filter(
                user=user,
                content_type=content_type,
                object_id=resource.id,
                permission_type='admin',
                is_active=True
            ).first()
            
            if admin_permission and admin_permission.is_valid():
                return True
        
        return False
    
    @classmethod
    def get_user_permissions(cls, user, resource_type=None):
        """
        Get all permissions for a user, optionally filtered by resource type.
        
        Args:
            user: User instance
            resource_type: Optional resource type filter
            
        Returns:
            QuerySet of permissions
        """
        queryset = cls.objects.filter(
            user=user,
            is_active=True
        ).select_related('content_type', 'granted_by')
        
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        
        return queryset
    
    @classmethod
    def get_resource_permissions(cls, resource):
        """
        Get all permissions for a specific resource.
        
        Args:
            resource: Resource instance
            
        Returns:
            QuerySet of permissions
        """
        content_type = ContentType.objects.get_for_model(resource)
        
        return cls.objects.filter(
            content_type=content_type,
            object_id=resource.id,
            is_active=True
        ).select_related('user', 'granted_by')
    
    @staticmethod
    def _get_resource_type(resource):
        """Get resource type string from resource instance."""
        resource_type_map = {
            'World': 'world',
            'Adventure': 'adventure',
            'Character': 'character',
            'RuleSet': 'rule_set',
            'TestWorld': 'world',
            'TestAdventure': 'adventure',
        }
        
        return resource_type_map.get(resource.__class__.__name__, 'unknown') 