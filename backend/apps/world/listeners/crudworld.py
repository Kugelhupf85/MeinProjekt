"""
World CRUD Event Listeners
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.world.models import World
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=World)
def world_post_save(sender, instance, created, **kwargs):
    """
    Handle world creation and update events
    """
    if created:
        logger.info(f"World created: {instance.entity_id} - {instance.name}")
        # Add any additional logic for world creation
    else:
        logger.info(f"World updated: {instance.entity_id} - {instance.name}")
        # Add any additional logic for world updates


@receiver(post_delete, sender=World)
def world_post_delete(sender, instance, **kwargs):
    """
    Handle world deletion events
    """
    logger.info(f"World deleted: {instance.entity_id} - {instance.name}")
    # Add any cleanup logic for world deletion 