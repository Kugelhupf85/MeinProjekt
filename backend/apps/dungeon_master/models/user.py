"""
Base user model for all Arcanovi users.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class ArcanoviUser(AbstractUser):
    """
    Base user model for all Arcanovi users (Players and Dungeon Masters).
    Extends Django's AbstractUser to provide authentication and basic user data.
    """
    
    entity_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Unique entity identifier with format: AU-{12_digit_id}"
    )
    
    display_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Display name for the user"
    )
    
    bio = models.TextField(
        max_length=2000,
        blank=True,
        help_text="Biography or description of the user"
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text="User avatar image"
    )
    
    # Override is_active to have our own help text
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this user account is active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the user was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the user was last updated"
    )
    
    class Meta:
        db_table = 'auth_arcanovi_user'
        verbose_name = 'Arcanovi User'
        verbose_name_plural = 'Arcanovi Users'
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        """
        Override save to generate entity_id if not present.
        """
        if not self.entity_id:
            # Generate 12-digit unique ID
            unique_id = str(uuid.uuid4().int)[:12]
            self.entity_id = f"AU-{unique_id}"
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        """
        String representation showing display name or username and entity_id.
        """
        name = self.display_name or self.username
        return f"{name} ({self.entity_id})"
    
    @property
    def full_name(self) -> str:
        """
        Return the full name of the user.
        """
        if self.display_name:
            return self.display_name
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def is_dungeon_master(self) -> bool:
        """
        Check if user has a dungeon master profile.
        """
        return hasattr(self, 'dm_profile')
    
    @property
    def is_player(self) -> bool:
        """
        Check if user has a player profile.
        """
        return hasattr(self, 'player_profile')


class PlayerProfile(models.Model):
    """
    Player-specific profile data and preferences.
    """
    
    user = models.OneToOneField(
        ArcanoviUser,
        on_delete=models.CASCADE,
        related_name='player_profile',
        help_text="Link to ArcanoviUser model"
    )
    
    # Player Preferences
    preferred_game_systems = models.JSONField(
        default=list,
        blank=True,
        help_text="List of preferred game systems"
    )
    
    character_creation_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="Character creation preferences and settings"
    )
    
    playstyle_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="Playstyle preferences and settings"
    )
    
    # Statistics
    campaigns_played = models.IntegerField(
        default=0,
        help_text="Number of campaigns played"
    )
    
    total_sessions = models.IntegerField(
        default=0,
        help_text="Total number of sessions played"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the profile was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the profile was last updated"
    )
    
    class Meta:
        db_table = 'dm_player_profile'
        verbose_name = 'Player Profile'
        verbose_name_plural = 'Player Profiles'
        ordering = ['-created_at']
        
    def __str__(self) -> str:
        return f"Player Profile: {self.user.full_name}"
    
    def add_preferred_game_system(self, system: str):
        """Add a preferred game system."""
        if system not in self.preferred_game_systems:
            self.preferred_game_systems.append(system)
            self.save()
    
    def remove_preferred_game_system(self, system: str):
        """Remove a preferred game system."""
        if system in self.preferred_game_systems:
            self.preferred_game_systems.remove(system)
            self.save()


class DungeonMasterProfile(models.Model):
    """
    Dungeon Master-specific profile data and preferences.
    Separated from base user to keep DM-specific functionality clean.
    """
    
    EXPERIENCE_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
        ('master', 'Master'),
    ]
    
    CONTENT_RATING_CHOICES = [
        ('family', 'Family'),
        ('teen', 'Teen'),
        ('mature', 'Mature'),
        ('adult', 'Adult'),
    ]
    
    user = models.OneToOneField(
        ArcanoviUser,
        on_delete=models.CASCADE,
        related_name='dm_profile',
        help_text="Link to ArcanoviUser model"
    )
    
    # DM Experience and Preferences
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='beginner',
        help_text="Experience level as a dungeon master"
    )
    
    strictness_level = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Strictness level from 1 (very lenient) to 10 (very strict)"
    )
    
    green_flags = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of positive preferences/styles"
    )
    
    red_flags = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of things to avoid/dislikes"
    )
    
    content_rating = models.CharField(
        max_length=10,
        choices=CONTENT_RATING_CHOICES,
        default='teen',
        help_text="Preferred content rating for games"
    )
    
    themes_preferences = models.JSONField(
        default=list,
        blank=True,
        help_text="Preferred themes and genres"
    )
    
    # Statistics
    campaigns_run = models.IntegerField(
        default=0,
        help_text="Number of campaigns run as DM"
    )
    
    total_sessions_run = models.IntegerField(
        default=0,
        help_text="Total number of sessions run as DM"
    )
    
    # Status
    is_public = models.BooleanField(
        default=False,
        help_text="Whether DM profile is publicly visible"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the profile was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the profile was last updated"
    )
    
    class Meta:
        db_table = 'dm_dungeonmaster_profile'
        verbose_name = 'Dungeon Master Profile'
        verbose_name_plural = 'Dungeon Master Profiles'
        ordering = ['-created_at']
        
    def __str__(self) -> str:
        return f"DM Profile: {self.user.full_name}"
    
    def add_green_flag(self, flag: str):
        """Add a positive preference/style flag."""
        if flag not in self.green_flags:
            self.green_flags.append(flag)
            self.save()
    
    def remove_green_flag(self, flag: str):
        """Remove a positive preference/style flag."""
        if flag in self.green_flags:
            self.green_flags.remove(flag)
            self.save()
    
    def add_red_flag(self, flag: str):
        """Add a negative preference/style flag."""
        if flag not in self.red_flags:
            self.red_flags.append(flag)
            self.save()
    
    def remove_red_flag(self, flag: str):
        """Remove a negative preference/style flag."""
        if flag in self.red_flags:
            self.red_flags.remove(flag)
            self.save()
    
    def add_theme_preference(self, theme: str):
        """Add a theme preference."""
        if theme not in self.themes_preferences:
            self.themes_preferences.append(theme)
            self.save()
    
    def remove_theme_preference(self, theme: str):
        """Remove a theme preference."""
        if theme in self.themes_preferences:
            self.themes_preferences.remove(theme)
            self.save() 