"""
World CRUD Services
"""

from typing import List, Dict, Optional, Any
from django.db import transaction, models
from django.core.exceptions import ValidationError
from apps.world.models import World
import logging

logger = logging.getLogger(__name__)


class WorldCRUDService:
    """
    Service class for World CRUD operations
    """
    
    @staticmethod
    def create_world(data: Dict[str, Any]) -> World:
        """
        Create a new world with validation
        
        Args:
            data: Dictionary containing world data
            
        Returns:
            World: Created world instance
            
        Raises:
            ValidationError: If data validation fails
        """
        try:
            with transaction.atomic():
                # Validate required fields
                required_fields = ['name', 'description']
                for field in required_fields:
                    if not data.get(field):
                        raise ValidationError(f"Field '{field}' is required")
                
                # Validate description length
                if len(data.get('description', '')) > 5000:
                    raise ValidationError("Description cannot exceed 5000 characters")
                
                # Create world instance
                world = World.objects.create(
                    name=data['name'],
                    description=data['description'],
                    general_mood=data.get('general_mood', ''),
                    important_locations=data.get('important_locations', []),
                    conventions=data.get('conventions', {}),
                    time_system=data.get('time_system', {}),
                    current_date=data.get('current_date', ''),
                    measurement_units=data.get('measurement_units', {}),
                    religions=data.get('religions', []),
                    magic_system=data.get('magic_system', {}),
                    political_systems=data.get('political_systems', []),
                    languages=data.get('languages', []),
                    history_timeline=data.get('history_timeline', []),
                    climate_zones=data.get('climate_zones', []),
                    natural_phenomena=data.get('natural_phenomena', []),
                    trade_routes=data.get('trade_routes', []),
                    conflicts_tensions=data.get('conflicts_tensions', []),
                    is_active=data.get('is_active', True)
                )
                
                logger.info(f"Created world: {world.entity_id}")
                return world
                
        except Exception as e:
            logger.error(f"Error creating world: {str(e)}")
            raise
    
    @staticmethod
    def get_world_by_id(world_id: str, generate_pill: bool = True) -> Optional[World]:
        """
        Retrieve a world by its entity ID
        
        Args:
            world_id: The entity ID of the world
            generate_pill: Whether to generate pill if not exists
            
        Returns:
            World instance or None if not found
        """
        try:
            world = World.objects.get(entity_id=world_id, is_active=True)
            
            # Generate pill on first access if requested
            if generate_pill and not world.pill:
                world.generate_pill()
                
            logger.info(f"Retrieved world: {world.entity_id}")
            return world
            
        except World.DoesNotExist:
            logger.warning(f"World not found: {world_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving world {world_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_world_by_pk(pk: int) -> Optional[World]:
        """
        Get world by primary key
        
        Args:
            pk: World primary key
            
        Returns:
            World instance or None
        """
        try:
            return World.objects.get(pk=pk, is_active=True)
        except World.DoesNotExist:
            return None
    
    @staticmethod
    def list_worlds(include_inactive: bool = False, generate_pills: bool = True) -> List[World]:
        """
        List all worlds with optional filtering
        
        Args:
            include_inactive: Whether to include inactive worlds
            generate_pills: Whether to generate pills for worlds that don't have them
            
        Returns:
            List of World instances
        """
        try:
            queryset = World.objects.all()
            
            if not include_inactive:
                queryset = queryset.filter(is_active=True)
            
            worlds = list(queryset.order_by('name'))
            
            # Generate pills for worlds that don't have them
            if generate_pills:
                for world in worlds:
                    if not world.pill:
                        world.generate_pill()
            
            logger.info(f"Listed {len(worlds)} worlds")
            return worlds
            
        except Exception as e:
            logger.error(f"Error listing worlds: {str(e)}")
            return []
    
    @staticmethod
    def update_world(world_id: str, data: Dict[str, Any]) -> Optional[World]:
        """
        Update world data
        
        Args:
            world_id: World entity_id
            data: Dictionary containing updated data
            
        Returns:
            Updated World instance or None
        """
        try:
            with transaction.atomic():
                world = WorldCRUDService.get_world_by_id(world_id)
                if not world:
                    return None
                
                # Update fields if provided
                updatable_fields = [
                    'name', 'description', 'general_mood', 'important_locations',
                    'conventions', 'time_system', 'current_date', 'measurement_units',
                    'religions', 'magic_system', 'political_systems', 'languages',
                    'history_timeline', 'climate_zones', 'natural_phenomena',
                    'trade_routes', 'conflicts_tensions', 'is_active'
                ]
                
                for field in updatable_fields:
                    if field in data:
                        # Validate description length
                        if field == 'description' and len(data[field]) > 5000:
                            raise ValidationError("Description cannot exceed 5000 characters")
                        setattr(world, field, data[field])
                
                world.save()
                logger.info(f"Updated world: {world.entity_id}")
                return world
                
        except Exception as e:
            logger.error(f"Error updating world {world_id}: {str(e)}")
            raise
    
    @staticmethod
    def delete_world(world_id: str, hard_delete: bool = False) -> bool:
        """
        Delete world (soft delete by default)
        
        Args:
            world_id: World entity_id
            hard_delete: Whether to permanently delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with transaction.atomic():
                world = WorldCRUDService.get_world_by_id(world_id)
                if not world:
                    return False
                
                if hard_delete:
                    world.delete()
                    logger.info(f"Hard deleted world: {world_id}")
                else:
                    world.is_active = False
                    world.save()
                    logger.info(f"Soft deleted world: {world_id}")
                
                return True
                
        except Exception as e:
            logger.error(f"Error deleting world {world_id}: {str(e)}")
            return False
    
    @staticmethod
    def search_worlds(query: str) -> List[World]:
        """
        Search worlds by name or description
        
        Args:
            query: Search query
            
        Returns:
            List of matching World instances
        """
        return list(
            World.objects.filter(
                models.Q(name__icontains=query) | 
                models.Q(description__icontains=query),
                is_active=True
            ).order_by('name')
        )
    
    @staticmethod
    def get_world_statistics(world_id: str) -> Dict:
        """
        Get comprehensive statistics for a world
        
        Args:
            world_id: The entity ID of the world
            
        Returns:
            Dictionary containing world statistics
        """
        try:
            world = World.objects.get(entity_id=world_id, is_active=True)
            
            # Ensure pill is generated for quick access
            if not world.pill:
                world.generate_pill()
            
            stats = {
                'world_info': {
                    'entity_id': world.entity_id,
                    'name': world.name,
                    'pill': world.pill,
                    'created_at': world.created_at,
                    'updated_at': world.updated_at
                },
                'region_count': world.region_count,
                'total_locations': world.total_locations,
                'active_adventures': world.get_active_adventures().count(),
                'regions': []
            }
            
            # Add region statistics
            for region in world.regions.filter(is_active=True):
                if not region.pill:
                    region.generate_pill()
                    
                region_stats = {
                    'entity_id': region.entity_id,
                    'name': region.name,
                    'pill': region.pill,
                    'location_count': region.location_count
                }
                stats['regions'].append(region_stats)
            
            logger.info(f"Generated statistics for world: {world_id}")
            return stats
            
        except World.DoesNotExist:
            logger.warning(f"World not found for statistics: {world_id}")
            return {}
        except Exception as e:
            logger.error(f"Error generating world statistics {world_id}: {str(e)}")
            return {}

    @staticmethod
    def refresh_world_pill(world_id: str) -> bool:
        """
        Force refresh the pill for a world
        
        Args:
            world_id: The entity ID of the world
            
        Returns:
            True if successful, False otherwise
        """
        try:
            world = World.objects.get(entity_id=world_id, is_active=True)
            world.refresh_pill()
            
            logger.info(f"Refreshed pill for world: {world_id}")
            return True
            
        except World.DoesNotExist:
            logger.warning(f"World not found for pill refresh: {world_id}")
            return False
        except Exception as e:
            logger.error(f"Error refreshing world pill {world_id}: {str(e)}")
            return False 