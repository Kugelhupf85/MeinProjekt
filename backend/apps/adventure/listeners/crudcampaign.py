"""
Django signals for Adventure CRUD events.
"""
import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from ..models import Adventure

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Adventure)
def log_adventure_created(sender, instance, created, **kwargs):
    """
    Log when an Adventure is created or updated.
    """
    if created:
        logger.info(
            f"Adventure created: {instance.entity_id} '{instance.name}' by DM {instance.dungeon_master.entity_id}"
        )
    else:
        logger.info(
            f"Adventure updated: {instance.entity_id} '{instance.name}' by DM {instance.dungeon_master.entity_id}"
        )


@receiver(post_delete, sender=Adventure)
def log_adventure_deleted(sender, instance, **kwargs):
    """
    Log when an Adventure is deleted.
    """
    logger.info(
        f"Adventure deleted: {instance.entity_id} '{instance.name}' by DM {instance.dungeon_master.entity_id}"
    )


@receiver(pre_save, sender=Adventure)
def validate_adventure_data(sender, instance, **kwargs):
    """
    Validate Adventure data before saving.
    """
    # Ensure JSON fields are properly formatted
    if not isinstance(instance.adventure_settings, dict):
        instance.adventure_settings = {}
    
    if not isinstance(instance.world_building, dict):
        instance.world_building = {}
    
    if not isinstance(instance.session_notes, list):
        instance.session_notes = []
    
    if not isinstance(instance.character_sheets, list):
        instance.character_sheets = []
    
    if not isinstance(instance.campaign_timeline, list):
        instance.campaign_timeline = []
    
    if not isinstance(instance.rules_modifications, dict):
        instance.rules_modifications = {}
    
    # Validate player count doesn't exceed maximum (10 based on model constraint)
    if instance.player_count > 10:
        logger.warning(
            f"Adventure {instance.entity_id} has player count ({instance.player_count}) "
            f"exceeding maximum allowed (10)"
        ) 