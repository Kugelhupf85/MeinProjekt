"""
Location CRUD Event Listeners
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.world.models import Location
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Location)
def location_post_save(sender, instance, created, **kwargs):
    """
    Handle location creation and update events
    """
    if created:
        logger.info(f"Location created: {instance.entity_id} - {instance.name} ({instance.location_type}) in {instance.region.name}")
        # Add any additional logic for location creation
    else:
        logger.info(f"Location updated: {instance.entity_id} - {instance.name}")
        # Add any additional logic for location updates


@receiver(post_delete, sender=Location)
def location_post_delete(sender, instance, **kwargs):
    """
    Handle location deletion events
    """
    logger.info(f"Location deleted: {instance.entity_id} - {instance.name}")
    # Add any cleanup logic for location deletion 