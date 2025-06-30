"""
Location CRUD Services
"""

from typing import List, Dict, Optional, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import models
from apps.world.models import Location, Region
import logging

logger = logging.getLogger(__name__)


class LocationCRUDService:
    """
    Service class for Location CRUD operations
    """
    
    @staticmethod
    def create_location(data: Dict[str, Any]) -> Location:
        """
        Create a new location with validation
        
        Args:
            data: Dictionary containing location data
            
        Returns:
            Location: Created location instance
            
        Raises:
            ValidationError: If data validation fails
        """
        try:
            with transaction.atomic():
                # Validate required fields
                required_fields = ['region_id', 'name', 'description']
                for field in required_fields:
                    if not data.get(field):
                        raise ValidationError(f"Field '{field}' is required")
                
                # Get region instance
                try:
                    region = Region.objects.get(entity_id=data['region_id'], is_active=True)
                except Region.DoesNotExist:
                    raise ValidationError(f"Region with ID {data['region_id']} not found")
                
                # Check for duplicate location name in region
                if Location.objects.filter(region=region, name=data['name'], is_active=True).exists():
                    raise ValidationError(f"Location '{data['name']}' already exists in region '{region.name}'")
                
                # Create location instance
                location = Location.objects.create(
                    region=region,
                    name=data['name'],
                    location_type=data.get('location_type', 'other'),
                    description=data['description'],
                    general_mood=data.get('general_mood', ''),
                    important_personalities=data.get('important_personalities', []),
                    services_available=data.get('services_available', []),
                    notable_features=data.get('notable_features', []),
                    secrets_hidden=data.get('secrets_hidden', []),
                    encounters_possible=data.get('encounters_possible', []),
                    items_treasures=data.get('items_treasures', []),
                    defenses_security=data.get('defenses_security', {}),
                    population_demographics=data.get('population_demographics', {}),
                    economic_activity=data.get('economic_activity', []),
                    connections_travel=data.get('connections_travel', []),
                    rumors_information=data.get('rumors_information', []),
                    seasonal_changes=data.get('seasonal_changes', {}),
                    size_scale=data.get('size_scale', ''),
                    accessibility=data.get('accessibility', ''),
                    current_events=data.get('current_events', []),
                    quest_opportunities=data.get('quest_opportunities', []),
                    is_active=data.get('is_active', True)
                )
                
                logger.info(f"Created location: {location.entity_id}")
                return location
                
        except Exception as e:
            logger.error(f"Error creating location: {str(e)}")
            raise
    
    @staticmethod
    def get_location_by_id(location_id: str, generate_pill: bool = True) -> Optional[Location]:
        """
        Retrieve a location by its entity ID
        
        Args:
            location_id: The entity ID of the location
            generate_pill: Whether to generate pill if not exists
            
        Returns:
            Location instance or None if not found
        """
        try:
            location = Location.objects.get(entity_id=location_id, is_active=True)
            
            # Generate pill on first access if requested
            if generate_pill and not location.pill:
                location.generate_pill()
                
            logger.info(f"Retrieved location: {location.entity_id}")
            return location
            
        except Location.DoesNotExist:
            logger.warning(f"Location not found: {location_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving location {location_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_location_by_pk(pk: int) -> Optional[Location]:
        """
        Get location by primary key
        
        Args:
            pk: Location primary key
            
        Returns:
            Location instance or None
        """
        try:
            return Location.objects.select_related('region', 'region__world').get(
                pk=pk, is_active=True
            )
        except Location.DoesNotExist:
            return None
    
    @staticmethod
    def list_locations(
        region_id: str = None, 
        world_id: str = None, 
        location_type: str = None,
        include_inactive: bool = False,
        generate_pills: bool = True
    ) -> List[Location]:
        """
        List locations with optional filtering
        
        Args:
            region_id: Optional region entity_id to filter by
            world_id: Optional world entity_id to filter by
            location_type: Optional location type to filter by
            include_inactive: Whether to include inactive locations
            generate_pills: Whether to generate pills for locations that don't have them
            
        Returns:
            List of Location instances
        """
        try:
            queryset = Location.objects.all()
            
            if region_id:
                queryset = queryset.filter(region__entity_id=region_id)
            elif world_id:
                queryset = queryset.filter(region__world__entity_id=world_id)
            
            if location_type:
                queryset = queryset.filter(location_type=location_type)
            
            if not include_inactive:
                queryset = queryset.filter(is_active=True)
            
            locations = list(queryset.order_by('region__world__name', 'region__name', 'name'))
            
            # Generate pills for locations that don't have them
            if generate_pills:
                for location in locations:
                    if not location.pill:
                        location.generate_pill()
            
            logger.info(f"Listed {len(locations)} locations")
            return locations
            
        except Exception as e:
            logger.error(f"Error listing locations: {str(e)}")
            return []
    
    @staticmethod
    def update_location(location_id: str, data: Dict[str, Any]) -> Optional[Location]:
        """
        Update location data
        
        Args:
            location_id: Location entity_id
            data: Dictionary containing updated data
            
        Returns:
            Updated Location instance or None
        """
        try:
            with transaction.atomic():
                location = LocationCRUDService.get_location_by_id(location_id)
                if not location:
                    return None
                
                # Check for duplicate name if name is being updated
                if 'name' in data and data['name'] != location.name:
                    if Location.objects.filter(
                        region=location.region, 
                        name=data['name'], 
                        is_active=True
                    ).exclude(pk=location.pk).exists():
                        raise ValidationError(f"Location '{data['name']}' already exists in region '{location.region.name}'")
                
                # Update fields if provided
                updatable_fields = [
                    'name', 'location_type', 'description', 'general_mood',
                    'important_personalities', 'services_available', 'notable_features',
                    'secrets_hidden', 'encounters_possible', 'items_treasures',
                    'defenses_security', 'population_demographics', 'economic_activity',
                    'connections_travel', 'rumors_information', 'seasonal_changes',
                    'size_scale', 'accessibility', 'current_events', 'quest_opportunities',
                    'is_active'
                ]
                
                for field in updatable_fields:
                    if field in data:
                        setattr(location, field, data[field])
                
                location.save()
                logger.info(f"Updated location: {location.entity_id}")
                return location
                
        except Exception as e:
            logger.error(f"Error updating location {location_id}: {str(e)}")
            raise
    
    @staticmethod
    def delete_location(location_id: str, hard_delete: bool = False) -> bool:
        """
        Delete location (soft delete by default)
        
        Args:
            location_id: Location entity_id
            hard_delete: Whether to permanently delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with transaction.atomic():
                location = LocationCRUDService.get_location_by_id(location_id)
                if not location:
                    return False
                
                if hard_delete:
                    location.delete()
                    logger.info(f"Hard deleted location: {location_id}")
                else:
                    location.is_active = False
                    location.save()
                    logger.info(f"Soft deleted location: {location_id}")
                
                return True
                
        except Exception as e:
            logger.error(f"Error deleting location {location_id}: {str(e)}")
            return False
    
    @staticmethod
    def search_locations(
        query: str, 
        region_id: Optional[str] = None,
        world_id: Optional[str] = None
    ) -> List[Location]:
        """
        Search locations by name or description
        
        Args:
            query: Search query
            region_id: Optional region entity_id to filter by
            world_id: Optional world entity_id to filter by
            
        Returns:
            List of matching Location instances
        """
        queryset = Location.objects.select_related('region', 'region__world').filter(
            models.Q(name__icontains=query) | 
            models.Q(description__icontains=query),
            is_active=True
        )
        
        if region_id:
            queryset = queryset.filter(region__entity_id=region_id)
        
        if world_id:
            queryset = queryset.filter(region__world__entity_id=world_id)
        
        return list(queryset.order_by('region__world__name', 'region__name', 'name'))
    
    @staticmethod
    def get_location_statistics(location_id: str) -> Optional[Dict[str, Any]]:
        """
        Get location statistics
        
        Args:
            location_id: Location entity_id
            
        Returns:
            Dictionary with location statistics
        """
        location = LocationCRUDService.get_location_by_id(location_id)
        if not location:
            return None
        
        return {
            'entity_id': location.entity_id,
            'name': location.name,
            'location_type': location.location_type,
            'region_name': location.region.name,
            'region_id': location.region.entity_id,
            'world_name': location.world.name,
            'world_id': location.world.entity_id,
            'full_path': location.full_path,
            'key_npcs_count': len(location.get_key_npcs()),
            'available_services_count': len(location.get_available_services()),
            'plot_hooks_count': len(location.get_current_plot_hooks()),
            'created_at': location.created_at,
            'updated_at': location.updated_at,
        }
    
    @staticmethod
    def get_locations_by_type(location_type: str, world_id: Optional[str] = None) -> List[Location]:
        """
        Get all locations of a specific type
        
        Args:
            location_type: Type of location to filter by
            world_id: Optional world entity_id to filter by
            
        Returns:
            List of Location instances
        """
        queryset = Location.objects.select_related('region', 'region__world').filter(
            location_type=location_type,
            is_active=True
        )
        
        if world_id:
            queryset = queryset.filter(region__world__entity_id=world_id)
        
        return list(queryset.order_by('region__world__name', 'region__name', 'name'))
    
    @staticmethod
    def refresh_location_pill(location_id: str) -> bool:
        """
        Force refresh the pill for a location
        
        Args:
            location_id: The entity ID of the location
            
        Returns:
            True if successful, False otherwise
        """
        try:
            location = Location.objects.get(entity_id=location_id, is_active=True)
            location.refresh_pill()
            
            logger.info(f"Refreshed pill for location: {location_id}")
            return True
            
        except Location.DoesNotExist:
            logger.warning(f"Location not found for pill refresh: {location_id}")
            return False
        except Exception as e:
            logger.error(f"Error refreshing location pill {location_id}: {str(e)}")
            return False 