"""
Django Signals for Permission Management.
Handles automatic permission setup and cleanup.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models.permission import Permission
from .utils import grant_permission_inheritance
from .logging import log_permission_grant, log_permission_inheritance

User = get_user_model()


@receiver(post_save, sender='world.World')
def world_created_permission_handler(sender, instance, created, **kwargs):
    """
    When a World is created, automatically grant admin permission to the creator.
    """
    if created:
        # Get the user who created the world (assuming it's in the request context)
        # For now, we'll need to handle this in the view or service layer
        # This is a placeholder for the automatic permission grant
        pass


@receiver(post_save, sender='adventure.Adventure')
def adventure_created_permission_handler(sender, instance, created, **kwargs):
    """
    When an Adventure is created, automatically grant permissions based on World permissions.
    """
    if created and hasattr(instance, 'world'):
        # Get all users with permissions on the world
        world_permissions = Permission.objects.filter(
            content_type__model='world',
            object_id=instance.world.id,
            is_active=True
        ).select_related('user')
        
        # Grant corresponding permissions on the adventure
        for world_perm in world_permissions:
            # Inherit permissions from world to adventure
            adventure_permission = Permission.grant_permission(
                user=world_perm.user,
                resource=instance,
                permission_type=world_perm.permission_type,
                granted_by=world_perm.granted_by,
                notes=f"Inherited from World {instance.world.id}"
            )
            
            # Log the inheritance
            log_permission_inheritance(
                user=world_perm.user,
                parent_resource=instance.world,
                child_resource=instance,
                permission_type=world_perm.permission_type,
                notes="Automatic inheritance on adventure creation"
            )


@receiver(post_delete, sender='world.World')
def world_deleted_permission_cleanup(sender, instance, **kwargs):
    """
    When a World is deleted, clean up all related permissions.
    """
    from django.contrib.contenttypes.models import ContentType
    
    # Get content type for World
    world_content_type = ContentType.objects.get_for_model(instance)
    
    # Delete all permissions for this world
    permissions = Permission.objects.filter(
        content_type=world_content_type,
        object_id=instance.id
    )
    
    count = permissions.count()
    permissions.delete()
    
    # Log the cleanup (if we had a logger available)
    print(f"Cleaned up {count} permissions for deleted world {instance.id}")


@receiver(post_delete, sender='adventure.Adventure')
def adventure_deleted_permission_cleanup(sender, instance, **kwargs):
    """
    When an Adventure is deleted, clean up all related permissions.
    """
    from django.contrib.contenttypes.models import ContentType
    
    # Get content type for Adventure
    adventure_content_type = ContentType.objects.get_for_model(instance)
    
    # Delete all permissions for this adventure
    permissions = Permission.objects.filter(
        content_type=adventure_content_type,
        object_id=instance.id
    )
    
    count = permissions.count()
    permissions.delete()
    
    # Log the cleanup
    print(f"Cleaned up {count} permissions for deleted adventure {instance.id}")


# Signal handlers for user role changes
@receiver(post_save, sender='core_user.UserWorldRole')
def user_world_role_changed_handler(sender, instance, created, **kwargs):
    """
    When a user's role in a world changes, update their permissions accordingly.
    """
    if created:
        # New role assignment - grant appropriate permissions
        if instance.role.name == 'world_admin':
            # World admin gets admin permissions on the world
            permission = Permission.grant_permission(
                user=instance.user,
                resource=instance.world,
                permission_type='admin',
                granted_by=instance.assigned_by,
                notes=f"Role assignment: {instance.role.display_name}"
            )
            
            # Log the permission grant
            log_permission_grant(
                user=instance.user,
                resource=instance.world,
                permission_type='admin',
                granted_by=instance.assigned_by,
                notes=f"Role assignment: {instance.role.display_name}"
            )
            
        elif instance.role.name == 'dungeon_master':
            # DM gets edit permissions on the world
            permission = Permission.grant_permission(
                user=instance.user,
                resource=instance.world,
                permission_type='edit',
                granted_by=instance.assigned_by,
                notes=f"Role assignment: {instance.role.display_name}"
            )
            
            log_permission_grant(
                user=instance.user,
                resource=instance.world,
                permission_type='edit',
                granted_by=instance.assigned_by,
                notes=f"Role assignment: {instance.role.display_name}"
            )
            
        elif instance.role.name == 'player':
            # Player gets view permissions on the world
            permission = Permission.grant_permission(
                user=instance.user,
                resource=instance.world,
                permission_type='view',
                granted_by=instance.assigned_by,
                notes=f"Role assignment: {instance.role.display_name}"
            )
            
            log_permission_grant(
                user=instance.user,
                resource=instance.world,
                permission_type='view',
                granted_by=instance.assigned_by,
                notes=f"Role assignment: {instance.role.display_name}"
            )
    
    elif not instance.is_active:
        # Role deactivated - revoke permissions
        from .utils import revoke_all_permissions
        
        count = revoke_all_permissions(instance.user, instance.world)
        
        # Log the permission revocation
        from .logging import log_permission_revoke
        log_permission_revoke(
            user=instance.user,
            resource=instance.world,
            permission_type='all',
            revoked_by=instance.assigned_by,
            notes=f"Role deactivation: {instance.role.display_name}"
        )


# Signal handlers for user deletion
@receiver(post_delete, sender=User)
def user_deleted_permission_cleanup(sender, instance, **kwargs):
    """
    When a user is deleted, clean up all their permissions.
    """
    # Delete all permissions for this user
    permissions = Permission.objects.filter(user=instance)
    count = permissions.count()
    permissions.delete()
    
    # Log the cleanup
    print(f"Cleaned up {count} permissions for deleted user {instance.email}")


# Management command signal handlers
def setup_permission_signals():
    """
    Setup all permission-related signals.
    Call this function to ensure signals are properly connected.
    """
    # This function can be called during app initialization
    # to ensure all signals are properly connected
    pass


def teardown_permission_signals():
    """
    Disconnect all permission-related signals.
    Call this function to clean up signal connections.
    """
    # Disconnect signals if needed
    post_save.disconnect(world_created_permission_handler, sender='world.World')
    post_save.disconnect(adventure_created_permission_handler, sender='adventure.Adventure')
    post_delete.disconnect(world_deleted_permission_cleanup, sender='world.World')
    post_delete.disconnect(adventure_deleted_permission_cleanup, sender='adventure.Adventure')
    post_save.disconnect(user_world_role_changed_handler, sender='core_user.UserWorldRole')
    post_delete.disconnect(user_deleted_permission_cleanup, sender=User) 