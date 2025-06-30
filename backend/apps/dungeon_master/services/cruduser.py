"""
CRUD operations for Dungeon Master user management.
"""
from typing import Optional, Dict, Any, List, Union
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from ..models import DungeonMaster


class DungeonMasterCRUD:
    """
    Static methods for Dungeon Master CRUD operations.
    Framework-agnostic service layer for user management.
    """
    
    @staticmethod
    def create_dungeon_master(
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        game_system_setting: Optional[Dict[str, Any]] = None,
        ui_settings: Optional[Dict[str, Any]] = None,
        ai_settings: Optional[Dict[str, Any]] = None
    ) -> DungeonMaster:
        """
        Create a new DungeonMaster with associated User.
        
        Args:
            username: Unique username for the user
            email: Email address for the user
            password: Password for the user
            first_name: Optional first name
            last_name: Optional last name
            game_system_setting: Optional game system configuration
            ui_settings: Optional UI preferences
            ai_settings: Optional AI integration settings
            
        Returns:
            Created DungeonMaster instance
            
        Raises:
            ValueError: If username or email already exists
            ValidationError: If data validation fails
        """
        # Validate unique constraints
        if User.objects.filter(username=username).exists():
            raise ValueError(f"Username '{username}' already exists")
        
        if User.objects.filter(email=email).exists():
            raise ValueError(f"Email '{email}' already exists")
        
        try:
            with transaction.atomic():
                # Create User
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create DungeonMaster profile
                dungeon_master = DungeonMaster.objects.create(
                    user=user,
                    game_system_setting=game_system_setting or {},
                    ui_settings=ui_settings or {},
                    ai_settings=ai_settings or {}
                )
                
                return dungeon_master
                
        except IntegrityError as e:
            raise ValueError(f"Database constraint violation: {e}")
    
    @staticmethod
    def get_dungeon_master_by_entity_id(entity_id: str) -> Optional[DungeonMaster]:
        """
        Retrieve DungeonMaster by entity_id.
        
        Args:
            entity_id: The entity_id to search for
            
        Returns:
            DungeonMaster instance or None if not found
        """
        try:
            return DungeonMaster.objects.select_related('user').get(
                entity_id=entity_id,
                is_active=True
            )
        except DungeonMaster.DoesNotExist:
            return None
    
    @staticmethod
    def get_dungeon_master_by_user_id(user_id: int) -> Optional[DungeonMaster]:
        """
        Retrieve DungeonMaster by user ID.
        
        Args:
            user_id: The Django User ID
            
        Returns:
            DungeonMaster instance or None if not found
        """
        try:
            return DungeonMaster.objects.select_related('user').get(
                user_id=user_id,
                is_active=True
            )
        except DungeonMaster.DoesNotExist:
            return None
    
    @staticmethod
    def list_dungeon_masters(
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None,
        active_only: bool = True
    ) -> List[DungeonMaster]:
        """
        List DungeonMasters with optional filtering.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            search: Optional search term for username/email
            active_only: Whether to include only active profiles
            
        Returns:
            List of DungeonMaster instances
        """
        queryset = DungeonMaster.objects.select_related('user')
        
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        if search:
            queryset = queryset.filter(
                user__username__icontains=search
            ) | queryset.filter(
                user__email__icontains=search
            ) | queryset.filter(
                user__first_name__icontains=search
            ) | queryset.filter(
                user__last_name__icontains=search
            )
        
        return list(queryset.order_by('-created_at')[offset:offset + limit])
    
    @staticmethod
    def update_dungeon_master_profile(
        entity_id: str,
        game_system_setting: Optional[Dict[str, Any]] = None,
        ui_settings: Optional[Dict[str, Any]] = None,
        ai_settings: Optional[Dict[str, Any]] = None
    ) -> Optional[DungeonMaster]:
        """
        Update DungeonMaster profile settings.
        
        Args:
            entity_id: The entity_id of the DungeonMaster
            game_system_setting: Updated game system settings
            ui_settings: Updated UI settings
            ai_settings: Updated AI settings
            
        Returns:
            Updated DungeonMaster instance or None if not found
        """
        try:
            dm = DungeonMaster.objects.get(entity_id=entity_id, is_active=True)
            
            if game_system_setting is not None:
                dm.game_system_setting = game_system_setting
            
            if ui_settings is not None:
                dm.ui_settings = ui_settings
            
            if ai_settings is not None:
                dm.ai_settings = ai_settings
            
            dm.save()
            return dm
            
        except DungeonMaster.DoesNotExist:
            return None
    
    @staticmethod
    def update_user_info(
        entity_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None
    ) -> Optional[DungeonMaster]:
        """
        Update User information for a DungeonMaster.
        
        Args:
            entity_id: The entity_id of the DungeonMaster
            first_name: Updated first name
            last_name: Updated last name
            email: Updated email address
            
        Returns:
            Updated DungeonMaster instance or None if not found
            
        Raises:
            ValueError: If email already exists for another user
        """
        try:
            dm = DungeonMaster.objects.select_related('user').get(
                entity_id=entity_id, 
                is_active=True
            )
            
            # Check email uniqueness if provided
            if email and User.objects.filter(email=email).exclude(id=dm.user.id).exists():
                raise ValueError(f"Email '{email}' already exists")
            
            # Update User fields
            if first_name is not None:
                dm.user.first_name = first_name
            
            if last_name is not None:
                dm.user.last_name = last_name
            
            if email is not None:
                dm.user.email = email
            
            dm.user.save()
            return dm
            
        except DungeonMaster.DoesNotExist:
            return None
    
    @staticmethod
    def update_individual_setting(
        entity_id: str,
        setting_type: str,
        key: str,
        value: Any
    ) -> Optional[DungeonMaster]:
        """
        Update an individual setting in one of the JSON fields.
        
        Args:
            entity_id: The entity_id of the DungeonMaster
            setting_type: Type of setting ('game_system', 'ui', 'ai')
            key: Setting key to update
            value: New value for the setting
            
        Returns:
            Updated DungeonMaster instance or None if not found
            
        Raises:
            ValueError: If setting_type is invalid
        """
        if setting_type not in ['game_system', 'ui', 'ai']:
            raise ValueError("setting_type must be 'game_system', 'ui', or 'ai'")
        
        try:
            dm = DungeonMaster.objects.get(entity_id=entity_id, is_active=True)
            
            if setting_type == 'game_system':
                dm.set_game_system_setting(key, value)
            elif setting_type == 'ui':
                dm.set_ui_setting(key, value)
            elif setting_type == 'ai':
                dm.set_ai_setting(key, value)
            
            return dm
            
        except DungeonMaster.DoesNotExist:
            return None
    
    @staticmethod
    def deactivate_dungeon_master(entity_id: str) -> bool:
        """
        Soft delete a DungeonMaster by setting is_active to False.
        
        Args:
            entity_id: The entity_id of the DungeonMaster to deactivate
            
        Returns:
            True if deactivated successfully, False if not found
        """
        try:
            dm = DungeonMaster.objects.get(entity_id=entity_id, is_active=True)
            dm.is_active = False
            dm.save()
            return True
            
        except DungeonMaster.DoesNotExist:
            return False
    
    @staticmethod
    def delete_dungeon_master(entity_id: str) -> bool:
        """
        Hard delete a DungeonMaster and associated User.
        WARNING: This will cascade delete all related data.
        
        Args:
            entity_id: The entity_id of the DungeonMaster to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        try:
            with transaction.atomic():
                dm = DungeonMaster.objects.select_related('user').get(entity_id=entity_id)
                user = dm.user
                
                # Delete DungeonMaster (cascade will handle related objects)
                dm.delete()
                
                # Delete User (if not referenced elsewhere)
                user.delete()
                
                return True
                
        except DungeonMaster.DoesNotExist:
            return False
    
    @staticmethod
    def get_dungeon_master_count() -> int:
        """
        Get total count of active DungeonMasters.
        
        Returns:
            Number of active DungeonMaster profiles
        """
        return DungeonMaster.objects.filter(is_active=True).count()
    
    @staticmethod
    def search_dungeon_masters(
        search_term: str,
        limit: int = 50
    ) -> List[DungeonMaster]:
        """
        Search DungeonMasters by username, email, or name.
        
        Args:
            search_term: Term to search for
            limit: Maximum number of results
            
        Returns:
            List of matching DungeonMaster instances
        """
        return list(
            DungeonMaster.objects.select_related('user').filter(
                is_active=True
            ).filter(
                user__username__icontains=search_term
            ).union(
                DungeonMaster.objects.select_related('user').filter(
                    is_active=True,
                    user__email__icontains=search_term
                )
            ).union(
                DungeonMaster.objects.select_related('user').filter(
                    is_active=True,
                    user__first_name__icontains=search_term
                )
            ).union(
                DungeonMaster.objects.select_related('user').filter(
                    is_active=True,
                    user__last_name__icontains=search_term
                )
            ).order_by('-created_at')[:limit]
        ) 