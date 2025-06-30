"""
Region CRUD Event Listeners
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.world.models import Region
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Region)
def region_post_save(sender, instance, created, **kwargs):
    """
    Handle region creation and update events
    """
    if created:
        logger.info(f"Region created: {instance.entity_id} - {instance.name} in {instance.world.name}")
        # Add any additional logic for region creation
    else:
        logger.info(f"Region updated: {instance.entity_id} - {instance.name}")
        # Add any additional logic for region updates


@receiver(post_delete, sender=Region)
def region_post_delete(sender, instance, **kwargs):
    """
    Handle region deletion events
    """
    logger.info(f"Region deleted: {instance.entity_id} - {instance.name}")
    # Add any cleanup logic for region deletion 