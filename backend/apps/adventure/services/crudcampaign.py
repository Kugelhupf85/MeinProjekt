"""
CRUD operations for Adventure campaign management.
"""
from typing import Optional, Dict, Any, List, Union
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from ..models import Adventure
from apps.dungeon_master.models import DungeonMaster


class AdventureCRUD:
    """
    Static methods for Adventure CRUD operations.
    Framework-agnostic service layer for campaign management.
    """
    
    @staticmethod
    def create_adventure(
        dungeon_master_entity_id: str,
        name: str,
        description: str = "",
        game_system: str = "D&D 5e",
        adventure_settings: Optional[Dict[str, Any]] = None,
        world_building: Optional[Dict[str, Any]] = None,
        player_count: int = 0
    ) -> Adventure:
        """
        Create a new Adventure for a DungeonMaster.
        
        Args:
            dungeon_master_entity_id: Entity ID of the DungeonMaster
            name: Name of the adventure/campaign
            description: Detailed description
            game_system: Game system being used
            adventure_settings: Initial adventure settings
            world_building: Initial world building data
            player_count: Number of players
            
        Returns:
            Created Adventure instance
            
        Raises:
            ValueError: If DM not found or already has max adventures
            ValidationError: If data validation fails
        """
        try:
            # Get DungeonMaster
            dm = DungeonMaster.objects.get(
                entity_id=dungeon_master_entity_id,
                is_active=True
            )
        except DungeonMaster.DoesNotExist:
            raise ValueError(f"DungeonMaster with entity_id '{dungeon_master_entity_id}' not found")
        
        # Check adventure limit (max 2 per DM)
        existing_count = Adventure.objects.filter(dungeon_master=dm).count()
        if existing_count >= 2:
            raise ValueError("DungeonMaster already has maximum number of adventures (2)")
        
        try:
            with transaction.atomic():
                adventure = Adventure.objects.create(
                    dungeon_master=dm,
                    name=name,
                    description=description,
                    game_system=game_system,
                    adventure_settings=adventure_settings or {},
                    world_building=world_building or {},
                    player_count=player_count
                )
                
                return adventure
                
        except IntegrityError as e:
            raise ValueError(f"Database constraint violation: {e}")
    
    @staticmethod
    def get_adventure_by_entity_id(entity_id: str) -> Optional[Adventure]:
        """
        Retrieve Adventure by entity_id.
        
        Args:
            entity_id: The entity_id to search for
            
        Returns:
            Adventure instance or None if not found
        """
        try:
            return Adventure.objects.select_related('dungeon_master__user').get(
                entity_id=entity_id
            )
        except Adventure.DoesNotExist:
            return None
    
    @staticmethod
    def list_adventures_by_dm(
        dungeon_master_entity_id: str,
        status_filter: Optional[str] = None
    ) -> List[Adventure]:
        """
        List Adventures for a specific DungeonMaster.
        
        Args:
            dungeon_master_entity_id: Entity ID of the DungeonMaster
            status_filter: Optional status filter
            
        Returns:
            List of Adventure instances
        """
        try:
            dm = DungeonMaster.objects.get(entity_id=dungeon_master_entity_id)
            queryset = Adventure.objects.filter(dungeon_master=dm)
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            return list(queryset.order_by('-created_at'))
            
        except DungeonMaster.DoesNotExist:
            return []
    
    @staticmethod
    def list_public_adventures(
        limit: int = 100,
        offset: int = 0,
        game_system_filter: Optional[str] = None
    ) -> List[Adventure]:
        """
        List public Adventures.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            game_system_filter: Optional game system filter
            
        Returns:
            List of Adventure instances
        """
        queryset = Adventure.objects.select_related('dungeon_master__user').filter(
            is_public=True
        )
        
        if game_system_filter:
            queryset = queryset.filter(game_system=game_system_filter)
        
        return list(queryset.order_by('-created_at')[offset:offset + limit])
    
    @staticmethod
    def update_adventure_basic_info(
        entity_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        game_system: Optional[str] = None,
        player_count: Optional[int] = None,
        is_public: Optional[bool] = None
    ) -> Optional[Adventure]:
        """
        Update basic Adventure information.
        
        Args:
            entity_id: The entity_id of the Adventure
            name: Updated name
            description: Updated description
            game_system: Updated game system
            player_count: Updated player count
            is_public: Updated public visibility
            
        Returns:
            Updated Adventure instance or None if not found
        """
        try:
            adventure = Adventure.objects.get(entity_id=entity_id)
            
            if name is not None:
                adventure.name = name
            
            if description is not None:
                adventure.description = description
            
            if game_system is not None:
                adventure.game_system = game_system
            
            if player_count is not None:
                adventure.player_count = player_count
            
            if is_public is not None:
                adventure.is_public = is_public
            
            adventure.save()
            return adventure
            
        except Adventure.DoesNotExist:
            return None
    
    @staticmethod
    def update_adventure_settings(
        entity_id: str,
        adventure_settings: Optional[Dict[str, Any]] = None,
        world_building: Optional[Dict[str, Any]] = None,
        rules_modifications: Optional[Dict[str, Any]] = None
    ) -> Optional[Adventure]:
        """
        Update Adventure JSON settings.
        
        Args:
            entity_id: The entity_id of the Adventure
            adventure_settings: Updated adventure settings
            world_building: Updated world building data
            rules_modifications: Updated rules modifications
            
        Returns:
            Updated Adventure instance or None if not found
        """
        try:
            adventure = Adventure.objects.get(entity_id=entity_id)
            
            if adventure_settings is not None:
                adventure.adventure_settings = adventure_settings
            
            if world_building is not None:
                adventure.world_building = world_building
            
            if rules_modifications is not None:
                adventure.rules_modifications = rules_modifications
            
            adventure.save()
            return adventure
            
        except Adventure.DoesNotExist:
            return None
    
    @staticmethod
    def update_adventure_status(
        entity_id: str,
        new_status: str
    ) -> Optional[Adventure]:
        """
        Update Adventure status with appropriate timestamp handling.
        
        Args:
            entity_id: The entity_id of the Adventure
            new_status: New status value
            
        Returns:
            Updated Adventure instance or None if not found
            
        Raises:
            ValueError: If status is invalid
        """
        valid_statuses = ['planning', 'active', 'paused', 'completed', 'archived']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        try:
            adventure = Adventure.objects.get(entity_id=entity_id)
            old_status = adventure.status
            
            adventure.update_status(new_status)
            return adventure
            
        except Adventure.DoesNotExist:
            return None
    
    @staticmethod
    def add_session_note(
        entity_id: str,
        session_note: Dict[str, Any]
    ) -> Optional[Adventure]:
        """
        Add a session note to an Adventure.
        
        Args:
            entity_id: The entity_id of the Adventure
            session_note: Session note data
            
        Returns:
            Updated Adventure instance or None if not found
        """
        try:
            adventure = Adventure.objects.get(entity_id=entity_id)
            adventure.add_session_note(session_note)
            return adventure
            
        except Adventure.DoesNotExist:
            return None
    
    @staticmethod
    def update_character_sheets(
        entity_id: str,
        character_sheets: List[Dict[str, Any]]
    ) -> Optional[Adventure]:
        """
        Update character sheets for an Adventure.
        
        Args:
            entity_id: The entity_id of the Adventure
            character_sheets: List of character sheet data
            
        Returns:
            Updated Adventure instance or None if not found
        """
        try:
            adventure = Adventure.objects.get(entity_id=entity_id)
            adventure.character_sheets = character_sheets
            adventure.save()
            return adventure
            
        except Adventure.DoesNotExist:
            return None
    
    @staticmethod
    def update_campaign_timeline(
        entity_id: str,
        timeline_events: List[Dict[str, Any]]
    ) -> Optional[Adventure]:
        """
        Update campaign timeline for an Adventure.
        
        Args:
            entity_id: The entity_id of the Adventure
            timeline_events: List of timeline events
            
        Returns:
            Updated Adventure instance or None if not found
        """
        try:
            adventure = Adventure.objects.get(entity_id=entity_id)
            adventure.campaign_timeline = timeline_events
            adventure.save()
            return adventure
            
        except Adventure.DoesNotExist:
            return None
    
    @staticmethod
    def set_adventure_setting(
        entity_id: str,
        key: str,
        value: Any
    ) -> Optional[Adventure]:
        """
        Set a specific adventure setting.
        
        Args:
            entity_id: The entity_id of the Adventure
            key: Setting key
            value: Setting value
            
        Returns:
            Updated Adventure instance or None if not found
        """
        try:
            adventure = Adventure.objects.get(entity_id=entity_id)
            adventure.set_adventure_setting(key, value)
            return adventure
            
        except Adventure.DoesNotExist:
            return None
    
    @staticmethod
    def delete_adventure(entity_id: str) -> bool:
        """
        Delete an Adventure.
        
        Args:
            entity_id: The entity_id of the Adventure to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        try:
            adventure = Adventure.objects.get(entity_id=entity_id)
            adventure.delete()
            return True
            
        except Adventure.DoesNotExist:
            return False
    
    @staticmethod
    def get_adventure_count_by_dm(dungeon_master_entity_id: str) -> int:
        """
        Get count of Adventures for a specific DungeonMaster.
        
        Args:
            dungeon_master_entity_id: Entity ID of the DungeonMaster
            
        Returns:
            Number of Adventures
        """
        try:
            dm = DungeonMaster.objects.get(entity_id=dungeon_master_entity_id)
            return Adventure.objects.filter(dungeon_master=dm).count()
        except DungeonMaster.DoesNotExist:
            return 0
    
    @staticmethod
    def search_adventures(
        search_term: str,
        public_only: bool = True,
        limit: int = 50
    ) -> List[Adventure]:
        """
        Search Adventures by name, description, or game system.
        
        Args:
            search_term: Term to search for
            public_only: Whether to search only public adventures
            limit: Maximum number of results
            
        Returns:
            List of matching Adventure instances
        """
        queryset = Adventure.objects.select_related('dungeon_master__user')
        
        if public_only:
            queryset = queryset.filter(is_public=True)
        
        return list(
            queryset.filter(
                name__icontains=search_term
            ).union(
                queryset.filter(
                    description__icontains=search_term
                )
            ).union(
                queryset.filter(
                    game_system__icontains=search_term
                )
            ).order_by('-created_at')[:limit]
        )
    
    @staticmethod
    def get_adventures_by_status(
        status: str,
        dungeon_master_entity_id: Optional[str] = None
    ) -> List[Adventure]:
        """
        Get Adventures filtered by status.
        
        Args:
            status: Status to filter by
            dungeon_master_entity_id: Optional DM filter
            
        Returns:
            List of Adventure instances
        """
        queryset = Adventure.objects.select_related('dungeon_master__user').filter(
            status=status
        )
        
        if dungeon_master_entity_id:
            try:
                dm = DungeonMaster.objects.get(entity_id=dungeon_master_entity_id)
                queryset = queryset.filter(dungeon_master=dm)
            except DungeonMaster.DoesNotExist:
                return []
        
        return list(queryset.order_by('-created_at'))
    
    @staticmethod
    def get_recent_adventures(
        limit: int = 10,
        public_only: bool = True
    ) -> List[Adventure]:
        """
        Get recently created or updated Adventures.
        
        Args:
            limit: Maximum number of results
            public_only: Whether to include only public adventures
            
        Returns:
            List of Adventure instances
        """
        queryset = Adventure.objects.select_related('dungeon_master__user')
        
        if public_only:
            queryset = queryset.filter(is_public=True)
        
        return list(queryset.order_by('-updated_at')[:limit])
    
    @staticmethod
    def validate_adventure_limit(dungeon_master_entity_id: str) -> bool:
        """
        Check if DungeonMaster can create another Adventure.
        
        Args:
            dungeon_master_entity_id: Entity ID of the DungeonMaster
            
        Returns:
            True if can create another Adventure, False otherwise
        """
        try:
            dm = DungeonMaster.objects.get(entity_id=dungeon_master_entity_id)
            current_count = Adventure.objects.filter(dungeon_master=dm).count()
            return current_count < 2
        except DungeonMaster.DoesNotExist:
            return False 