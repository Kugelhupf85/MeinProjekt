"""
User Settings model for Dungeon Master UI/UX and AI preferences.
"""
from django.db import models
from .dungeonmaster import DungeonMaster


class UserSettings(models.Model):
    """
    User Settings model for storing UI/UX and AI preferences.
    
    This model stores:
    - UI/UX settings (theme, language, notifications, etc.)
    - AI assistant settings (language, features, memory)
    - Feature flags and experimental features
    - Privacy and security preferences
    """
    
    dungeonmaster = models.OneToOneField(
        DungeonMaster,
        on_delete=models.CASCADE,
        related_name='settings',
        help_text="Link to DungeonMaster profile"
    )
    
    # UI/UX Settings
    ui_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON configuration for UI/UX preferences"
    )
    
    # AI Assistant Settings
    ai_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON configuration for AI assistant preferences"
    )
    
    # Feature Flags & Experimental Features
    feature_flags = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON configuration for feature flags and experimental features"
    )
    
    # Privacy & Security Preferences
    privacy_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON configuration for privacy and security preferences"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the settings were created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the settings were last updated"
    )
    
    class Meta:
        db_table = 'dm_user_settings'
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'
        ordering = ['-updated_at']
    
    def __str__(self) -> str:
        """
        String representation showing the associated dungeon master.
        """
        return f"Settings for {self.dungeonmaster}"
    
    @classmethod
    def get_default_ui_settings(cls):
        """Return default UI settings structure."""
        return {
            "theme": "dark",
            "language": "de",
            "timezone": "UTC",
            "date_format": "YYYY-MM-DD",
            "time_format": "24h",
            "compact_mode": False,
            "show_tooltips": True,
            "auto_save_interval": 300,
            "notification_preferences": {
                "email": True,
                "browser": True,
                "sound": False
            },
            "dashboard_layout": {
                "widget_order": [],
                "collapsed_sections": []
            },
            "accessibility": {
                "high_contrast": False,
                "large_text": False,
                "screen_reader_support": False
            }
        }
    
    @classmethod
    def get_default_ai_settings(cls):
        """Return default AI settings structure."""
        return {
            "language": "de",
            "memory_retention": True,
            "specialized_features": {
                "world_building_assistant": True,
                "npc_generator": True,
                "plot_suggestions": True,
                "rule_clarifications": True,
                "session_summaries": True
            }
        }
    
    @classmethod
    def get_default_feature_flags(cls):
        """Return default feature flags structure."""
        return {
            "beta_features": False
        }
    
    @classmethod
    def get_default_privacy_settings(cls):
        """Return default privacy settings structure."""
        return {
            "profile_visibility": "private"
        }
    
    def save(self, *args, **kwargs):
        """
        Override save to set default values if not present.
        """
        if not self.ui_settings:
            self.ui_settings = self.get_default_ui_settings()
        if not self.ai_settings:
            self.ai_settings = self.get_default_ai_settings()
        if not self.feature_flags:
            self.feature_flags = self.get_default_feature_flags()
        if not self.privacy_settings:
            self.privacy_settings = self.get_default_privacy_settings()
        super().save(*args, **kwargs)
    
    def get_ui_setting(self, key: str, default=None):
        """
        Get a specific UI setting.
        
        Args:
            key: The setting key to retrieve (supports dot notation)
            default: Default value if key not found
            
        Returns:
            The setting value or default
        """
        keys = key.split('.')
        value = self.ui_settings
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set_ui_setting(self, key: str, value):
        """
        Set a specific UI setting.
        
        Args:
            key: The setting key to set (supports dot notation)
            value: The value to set
        """
        keys = key.split('.')
        current = self.ui_settings
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        self.save()
    
    def get_ai_setting(self, key: str, default=None):
        """
        Get a specific AI setting.
        
        Args:
            key: The setting key to retrieve (supports dot notation)
            default: Default value if key not found
            
        Returns:
            The setting value or default
        """
        keys = key.split('.')
        value = self.ai_settings
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set_ai_setting(self, key: str, value):
        """
        Set a specific AI setting.
        
        Args:
            key: The setting key to set (supports dot notation)
            value: The value to set
        """
        keys = key.split('.')
        current = self.ai_settings
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        self.save()
    
    def get_feature_flag(self, key: str, default=False):
        """
        Get a specific feature flag.
        
        Args:
            key: The feature flag key to retrieve
            default: Default value if key not found
            
        Returns:
            The feature flag value or default
        """
        return self.feature_flags.get(key, default)
    
    def set_feature_flag(self, key: str, value: bool):
        """
        Set a specific feature flag.
        
        Args:
            key: The feature flag key to set
            value: The boolean value to set
        """
        self.feature_flags[key] = value
        self.save()
    
    def get_privacy_setting(self, key: str, default=None):
        """
        Get a specific privacy setting.
        
        Args:
            key: The privacy setting key to retrieve
            default: Default value if key not found
            
        Returns:
            The privacy setting value or default
        """
        return self.privacy_settings.get(key, default)
    
    def set_privacy_setting(self, key: str, value):
        """
        Set a specific privacy setting.
        
        Args:
            key: The privacy setting key to set
            value: The value to set
        """
        self.privacy_settings[key] = value
        self.save() 