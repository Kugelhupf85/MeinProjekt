"""
Dungeon Master user model extending Django's User model.
"""
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class DungeonMaster(models.Model):
    """
    Dungeon Master profile extending Django User with game-specific settings.
    
    This model stores the core DM profile information including:
    - Basic profile data (display name, bio, experience)
    - Game mastering preferences (strictness, flags, themes)
    - Content preferences and visibility settings
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
    
    entity_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Unique entity identifier with format: DM-{12_digit_id}"
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='dungeon_master_profile',
        help_text="Link to Django User model"
    )
    
    # Core DM Profile Information
    display_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Display name for the dungeon master"
    )
    
    bio = models.TextField(
        blank=True,
        null=True,
        max_length=2000,
        help_text="Biography or description of the dungeon master"
    )
    
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='beginner',
        help_text="Experience level as a dungeon master"
    )
    
    # Game Mastering Style & Preferences
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
    
    # Content Preferences
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
    
    # Status and Metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this dungeon master profile is active"
    )
    
    is_public = models.BooleanField(
        default=False,
        help_text="Whether profile is publicly visible"
    )
    
    last_active = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the dungeon master was last active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the dungeon master profile was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the dungeon master profile was last updated"
    )
    
    class Meta:
        db_table = 'dm_user_dungeonmaster'
        verbose_name = 'Dungeon Master'
        verbose_name_plural = 'Dungeon Masters'
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        """
        Override save to generate entity_id if not present.
        """
        if not self.entity_id:
            # Generate 12-digit unique ID
            unique_id = str(uuid.uuid4().int)[:12]
            self.entity_id = f"DM-{unique_id}"
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        """
        String representation showing display name or username and entity_id.
        """
        name = self.display_name or self.user.username
        return f"{name} ({self.entity_id})"
    
    @property
    def full_name(self) -> str:
        """
        Return the full name of the user.
        """
        if self.display_name:
            return self.display_name
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    @property
    def email(self) -> str:
        """
        Return the email address of the user.
        """
        return self.user.email
    
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