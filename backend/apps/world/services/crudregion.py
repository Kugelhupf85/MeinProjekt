"""
Region CRUD Services
"""

from typing import List, Dict, Optional, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import models
from apps.world.models import Region, World
import logging

logger = logging.getLogger(__name__)


class RegionCRUDService:
    """
    Service class for Region CRUD operations
    """
    
    @staticmethod
    def create_region(data: Dict[str, Any]) -> Region:
        """
        Create a new region with validation
        
        Args:
            data: Dictionary containing region data
            
        Returns:
            Region: Created region instance
            
        Raises:
            ValidationError: If data validation fails
        """
        try:
            with transaction.atomic():
                # Validate required fields
                required_fields = ['world_id', 'name', 'description']
                for field in required_fields:
                    if not data.get(field):
                        raise ValidationError(f"Field '{field}' is required")
                
                # Get world instance
                try:
                    world = World.objects.get(entity_id=data['world_id'], is_active=True)
                except World.DoesNotExist:
                    raise ValidationError(f"World with ID {data['world_id']} not found")
                
                # Check for duplicate region name in world
                if Region.objects.filter(world=world, name=data['name'], is_active=True).exists():
                    raise ValidationError(f"Region '{data['name']}' already exists in world '{world.name}'")
                
                # Create region instance
                region = Region.objects.create(
                    world=world,
                    name=data['name'],
                    description=data['description'],
                    general_mood=data.get('general_mood', ''),
                    currencies=data.get('currencies', []),
                    important_personalities=data.get('important_personalities', []),
                    religions=data.get('religions', []),
                    government_type=data.get('government_type', {}),
                    cultural_traits=data.get('cultural_traits', []),
                    major_settlements=data.get('major_settlements', []),
                    natural_resources=data.get('natural_resources', []),
                    trade_specialties=data.get('trade_specialties', []),
                    threats_dangers=data.get('threats_dangers', []),
                    climate_weather=data.get('climate_weather', {}),
                    laws_customs=data.get('laws_customs', []),
                    festivals_events=data.get('festivals_events', []),
                    military_forces=data.get('military_forces', {}),
                    terrain_type=data.get('terrain_type', ''),
                    size_description=data.get('size_description', ''),
                    is_active=data.get('is_active', True)
                )
                
                logger.info(f"Created region: {region.entity_id}")
                return region
                
        except Exception as e:
            logger.error(f"Error creating region: {str(e)}")
            raise
    
    @staticmethod
    def get_region_by_id(region_id: str, generate_pill: bool = True) -> Optional[Region]:
        """
        Retrieve a region by its entity ID
        
        Args:
            region_id: The entity ID of the region
            generate_pill: Whether to generate pill if not exists
            
        Returns:
            Region instance or None if not found
        """
        try:
            region = Region.objects.get(entity_id=region_id, is_active=True)
            
            # Generate pill on first access if requested
            if generate_pill and not region.pill:
                region.generate_pill()
                
            logger.info(f"Retrieved region: {region.entity_id}")
            return region
            
        except Region.DoesNotExist:
            logger.warning(f"Region not found: {region_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving region {region_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_region_by_pk(pk: int) -> Optional[Region]:
        """
        Get region by primary key
        
        Args:
            pk: Region primary key
            
        Returns:
            Region instance or None
        """
        try:
            return Region.objects.select_related('world').get(pk=pk, is_active=True)
        except Region.DoesNotExist:
            return None
    
    @staticmethod
    def list_regions(world_id: str = None, include_inactive: bool = False, generate_pills: bool = True) -> List[Region]:
        """
        List regions with optional filtering
        
        Args:
            world_id: Optional world entity_id to filter by
            include_inactive: Whether to include inactive regions
            generate_pills: Whether to generate pills for regions that don't have them
            
        Returns:
            List of Region instances
        """
        try:
            queryset = Region.objects.all()
            
            if world_id:
                queryset = queryset.filter(world__entity_id=world_id)
            
            if not include_inactive:
                queryset = queryset.filter(is_active=True)
            
            regions = list(queryset.order_by('world__name', 'name'))
            
            # Generate pills for regions that don't have them
            if generate_pills:
                for region in regions:
                    if not region.pill:
                        region.generate_pill()
            
            logger.info(f"Listed {len(regions)} regions")
            return regions
            
        except Exception as e:
            logger.error(f"Error listing regions: {str(e)}")
            return []
    
    @staticmethod
    def update_region(region_id: str, data: Dict[str, Any]) -> Optional[Region]:
        """
        Update region data
        
        Args:
            region_id: Region entity_id
            data: Dictionary containing updated data
            
        Returns:
            Updated Region instance or None
        """
        try:
            with transaction.atomic():
                region = RegionCRUDService.get_region_by_id(region_id)
                if not region:
                    return None
                
                # Check for duplicate name if name is being updated
                if 'name' in data and data['name'] != region.name:
                    if Region.objects.filter(
                        world=region.world, 
                        name=data['name'], 
                        is_active=True
                    ).exclude(pk=region.pk).exists():
                        raise ValidationError(f"Region '{data['name']}' already exists in world '{region.world.name}'")
                
                # Update fields if provided
                updatable_fields = [
                    'name', 'description', 'general_mood', 'currencies',
                    'important_personalities', 'religions', 'government_type',
                    'cultural_traits', 'major_settlements', 'natural_resources',
                    'trade_specialties', 'threats_dangers', 'climate_weather',
                    'laws_customs', 'festivals_events', 'military_forces',
                    'terrain_type', 'size_description', 'is_active'
                ]
                
                for field in updatable_fields:
                    if field in data:
                        setattr(region, field, data[field])
                
                region.save()
                logger.info(f"Updated region: {region.entity_id}")
                return region
                
        except Exception as e:
            logger.error(f"Error updating region {region_id}: {str(e)}")
            raise
    
    @staticmethod
    def delete_region(region_id: str, hard_delete: bool = False) -> bool:
        """
        Delete region (soft delete by default)
        
        Args:
            region_id: Region entity_id
            hard_delete: Whether to permanently delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with transaction.atomic():
                region = RegionCRUDService.get_region_by_id(region_id)
                if not region:
                    return False
                
                if hard_delete:
                    region.delete()
                    logger.info(f"Hard deleted region: {region_id}")
                else:
                    region.is_active = False
                    region.save()
                    logger.info(f"Soft deleted region: {region_id}")
                
                return True
                
        except Exception as e:
            logger.error(f"Error deleting region {region_id}: {str(e)}")
            return False
    
    @staticmethod
    def search_regions(query: str, world_id: Optional[str] = None) -> List[Region]:
        """
        Search regions by name or description
        
        Args:
            query: Search query
            world_id: Optional world entity_id to filter by
            
        Returns:
            List of matching Region instances
        """
        queryset = Region.objects.select_related('world').filter(
            models.Q(name__icontains=query) | 
            models.Q(description__icontains=query),
            is_active=True
        )
        
        if world_id:
            queryset = queryset.filter(world__entity_id=world_id)
        
        return list(queryset.order_by('world__name', 'name'))
    
    @staticmethod
    def get_region_statistics(region_id: str) -> Optional[Dict[str, Any]]:
        """
        Get region statistics
        
        Args:
            region_id: Region entity_id
            
        Returns:
            Dictionary with region statistics
        """
        region = RegionCRUDService.get_region_by_id(region_id)
        if not region:
            return None
        
        return {
            'entity_id': region.entity_id,
            'name': region.name,
            'world_name': region.world.name,
            'world_id': region.world.entity_id,
            'location_count': region.location_count,
            'major_personalities_count': len(region.get_major_personalities()),
            'primary_currency': region.get_primary_currency(),
            'created_at': region.created_at,
            'updated_at': region.updated_at,
        }
    
    @staticmethod
    def refresh_region_pill(region_id: str) -> bool:
        """
        Force refresh the pill for a region
        
        Args:
            region_id: The entity ID of the region
            
        Returns:
            True if successful, False otherwise
        """
        try:
            region = Region.objects.get(entity_id=region_id, is_active=True)
            region.refresh_pill()
            
            logger.info(f"Refreshed pill for region: {region_id}")
            return True
            
        except Region.DoesNotExist:
            logger.warning(f"Region not found for pill refresh: {region_id}")
            return False
        except Exception as e:
            logger.error(f"Error refreshing region pill {region_id}: {str(e)}")
            return False 