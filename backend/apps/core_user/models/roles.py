"""
Role System for Arcanovi.
Provides context-specific role assignments (user-world-role combinations).
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Role(models.Model):
    """
    Standard roles in the Arcanovi system.
    """
    
    ROLE_CHOICES = [
        ('player', _('Player')),
        ('dungeon_master', _('Dungeon Master')),
        ('world_admin', _('World Administrator')),
    ]
    
    name = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        unique=True,
        help_text=_('The role name')
    )
    
    display_name = models.CharField(
        max_length=100,
        help_text=_('Human-readable role name')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Description of what this role can do')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this role is available for assignment')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Timestamp when the role was created')
    )
    
    class Meta:
        db_table = 'core_role'
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        ordering = ['name']
    
    def __str__(self):
        return self.display_name


class UserWorldRole(models.Model):
    """
    Context-specific role assignments.
    A user can have different roles in different worlds.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='world_roles',
        help_text=_('The user who has this role')
    )
    
    world = models.ForeignKey(
        'world.World',  # Reference to world app
        on_delete=models.CASCADE,
        related_name='user_roles',
        help_text=_('The world where this role applies')
    )
    
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        help_text=_('The role assigned to the user')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this role assignment is currently active')
    )
    
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Timestamp when the role was assigned')
    )
    
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles',
        help_text=_('The user who assigned this role')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('Timestamp when the role assignment was last updated')
    )
    
    class Meta:
        db_table = 'core_user_world_role'
        verbose_name = _('User World Role')
        verbose_name_plural = _('User World Roles')
        unique_together = ['user', 'world', 'role']
        ordering = ['world', 'user', 'role']
    
    def __str__(self):
        return f"{self.user.email} - {self.role.display_name} in {self.world.name}"
    
    @classmethod
    def assign_role(cls, user, world, role_name, assigned_by=None):
        """
        Assign a role to a user in a specific world.
        
        Args:
            user: User instance
            world: World instance
            role_name: String name of the role
            assigned_by: User who is assigning the role (optional)
        
        Returns:
            UserWorldRole instance
        """
        role = Role.objects.get(name=role_name, is_active=True)
        user_world_role, created = cls.objects.get_or_create(
            user=user,
            world=world,
            role=role,
            defaults={
                'assigned_by': assigned_by,
                'is_active': True,
            }
        )
        
        if not created and not user_world_role.is_active:
            user_world_role.is_active = True
            user_world_role.assigned_by = assigned_by
            user_world_role.save(update_fields=['is_active', 'assigned_by', 'updated_at'])
        
        return user_world_role
    
    @classmethod
    def remove_role(cls, user, world, role_name):
        """
        Remove a role from a user in a specific world.
        """
        try:
            role = Role.objects.get(name=role_name)
            user_world_role = cls.objects.get(user=user, world=world, role=role)
            user_world_role.is_active = False
            user_world_role.save(update_fields=['is_active', 'updated_at'])
            return True
        except (Role.DoesNotExist, cls.DoesNotExist):
            return False
    
    @classmethod
    def has_role_in_world(cls, user, world, role_name):
        """
        Check if a user has a specific role in a world.
        """
        try:
            role = Role.objects.get(name=role_name, is_active=True)
            return cls.objects.filter(
                user=user,
                world=world,
                role=role,
                is_active=True
            ).exists()
        except Role.DoesNotExist:
            return False
    
    @classmethod
    def get_user_roles_in_world(cls, user, world):
        """
        Get all active roles for a user in a specific world.
        """
        return cls.objects.filter(
            user=user,
            world=world,
            is_active=True
        ).select_related('role')
    
    @classmethod
    def get_worlds_for_user_role(cls, user, role_name):
        """
        Get all worlds where a user has a specific role.
        """
        try:
            role = Role.objects.get(name=role_name, is_active=True)
            return cls.objects.filter(
                user=user,
                role=role,
                is_active=True
            ).select_related('world')
        except Role.DoesNotExist:
            return cls.objects.none() 