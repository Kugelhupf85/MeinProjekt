"""
Django signals for Dungeon Master CRUD events.
"""
import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from ..models import DungeonMaster

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DungeonMaster)
def log_dungeon_master_created(sender, instance, created, **kwargs):
    """
    Log when a DungeonMaster is created or updated.
    """
    if created:
        logger.info(
            f"DungeonMaster created: {instance.entity_id} for user {instance.user.username}"
        )
    else:
        logger.info(
            f"DungeonMaster updated: {instance.entity_id} for user {instance.user.username}"
        )


@receiver(post_delete, sender=DungeonMaster)
def log_dungeon_master_deleted(sender, instance, **kwargs):
    """
    Log when a DungeonMaster is deleted.
    """
    logger.info(
        f"DungeonMaster deleted: {instance.entity_id} for user {instance.user.username}"
    )


@receiver(pre_save, sender=DungeonMaster)
def validate_dungeon_master_data(sender, instance, **kwargs):
    """
    Validate DungeonMaster data before saving.
    """
    # Ensure JSON fields are properly formatted
    if not isinstance(instance.green_flags, list):
        instance.green_flags = []
    
    if not isinstance(instance.red_flags, list):
        instance.red_flags = []
    
    if not isinstance(instance.themes_preferences, list):
        instance.themes_preferences = []
    
    # Validate strictness level
    if instance.strictness_level < 1:
        instance.strictness_level = 1
    elif instance.strictness_level > 10:
        instance.strictness_level = 10


@receiver(post_save, sender=User)
def create_dungeon_master_profile(sender, instance, created, **kwargs):
    """
    Automatically create DungeonMaster profile for new users (optional).
    This is disabled by default - users must explicitly create DM profiles.
    """
    # Uncomment the following lines if you want automatic DM profile creation
    # if created:
    #     DungeonMaster.objects.create(user=instance)
    pass 