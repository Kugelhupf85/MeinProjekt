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
        return f"Settings for {self.dungeonmaster}"
    
    def get_ui_setting(self, key: str, default=None):
        """Get a specific UI setting."""
        return self.ui_settings.get(key, default)
    
    def set_ui_setting(self, key: str, value):
        """Set a specific UI setting."""
        self.ui_settings[key] = value
        self.save()
    
    def get_ai_setting(self, key: str, default=None):
        """Get a specific AI setting."""
        return self.ai_settings.get(key, default)
    
    def set_ai_setting(self, key: str, value):
        """Set a specific AI setting."""
        self.ai_settings[key] = value
        self.save()
    
    def get_feature_flag(self, key: str, default=False):
        """Get a specific feature flag."""
        return self.feature_flags.get(key, default)
    
    def set_feature_flag(self, key: str, value: bool):
        """Set a specific feature flag."""
        self.feature_flags[key] = value
        self.save()
    
    def get_privacy_setting(self, key: str, default=None):
        """Get a specific privacy setting."""
        return self.privacy_settings.get(key, default)
    
    def set_privacy_setting(self, key: str, value):
        """Set a specific privacy setting."""
        self.privacy_settings[key] = value
        self.save() 