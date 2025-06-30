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
    if not isinstance(instance.game_system_setting, dict):
        instance.game_system_setting = {}
    
    if not isinstance(instance.ui_settings, dict):
        instance.ui_settings = {}
    
    if not isinstance(instance.ai_settings, dict):
        instance.ai_settings = {}


@receiver(post_save, sender=User)
def create_dungeon_master_profile(sender, instance, created, **kwargs):
    """
    Automatically create DungeonMaster profile when a User is created.
    This is optional - can be removed if profiles should be created manually.
    """
    # Uncomment the following lines if you want automatic profile creation
    # if created:
    #     DungeonMaster.objects.create(user=instance)
    #     logger.info(f"Auto-created DungeonMaster profile for user {instance.username}")
    pass 