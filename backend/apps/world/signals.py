"""
Django Signals for World App
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.world.models.modelworld import World, WorldAPIKeys, WorldParty, WorldPartyMembership
from apps.permissions.models.permission import Permission

User = get_user_model()


@receiver(post_save, sender=World)
def create_world_api_keys(sender, instance, created, **kwargs):
    """
    Automatically create WorldAPIKeys when a World is created.
    """
    if created:
        WorldAPIKeys.objects.create(world=instance)


@receiver(post_save, sender=World)
def create_world_party(sender, instance, created, **kwargs):
    """
    Automatically create WorldParty when a World is created.
    """
    if created:
        # Create party with default name based on world name
        party_name = f"Party of {instance.name}"
        WorldParty.objects.create(
            world=instance,
            name=party_name,
            creator=instance.created_by
        )


@receiver(post_save, sender=WorldParty)
def create_creator_membership(sender, instance, created, **kwargs):
    """
    Automatically create WorldPartyMembership for the creator when a WorldParty is created.
    """
    if created and instance.creator:
        # Create membership for creator with DM role
        membership = WorldPartyMembership.objects.create(
            user=instance.creator,
            party=instance,
            role='dungeon_master',
            status='active'
        )
        
        # Grant admin permission to creator for the world
        Permission.grant_permission(
            user=instance.creator,
            resource=instance.world,
            permission_type='admin',
            granted_by=instance.creator
        )


@receiver(post_save, sender=WorldPartyMembership)
def handle_dm_role_change(sender, instance, created, **kwargs):
    """
    Handle permission changes when DM role changes.
    """
    if instance.role == 'dungeon_master':
        # Grant admin permission to DM
        Permission.grant_permission(
            user=instance.user,
            resource=instance.party.world,
            permission_type='admin',
            granted_by=instance.user
        )
    else:
        # Remove admin permission if role changes from DM
        Permission.revoke_permission(
            user=instance.user,
            resource=instance.party.world,
            permission_type='admin'
        )


@receiver(post_delete, sender=World)
def cleanup_world_data(sender, instance, **kwargs):
    """
    Clean up related data when a World is deleted.
    """
    # WorldAPIKeys and WorldParty will be automatically deleted due to CASCADE
    # Permission cleanup is handled by the Permission model's post_delete signal
    pass


@receiver(post_delete, sender=WorldPartyMembership)
def cleanup_membership_permissions(sender, instance, **kwargs):
    """
    Clean up permissions when a party membership is deleted.
    """
    # Remove all permissions for this user on this world
    Permission.revoke_all_permissions(
        user=instance.user,
        resource=instance.party.world
    ) 