"""
Adventure model for campaign management.
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.dungeon_master.models import DungeonMaster


class Adventure(models.Model):
    """
    Adventure model representing a campaign or single adventure.
    
    Each dungeon master can create up to 2 adventures with comprehensive
    campaign management features and JSON-based configuration.
    """
    
    entity_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Unique entity identifier with format: adv-{12_digit_id}"
    )
    
    dungeon_master = models.ForeignKey(
        DungeonMaster,
        on_delete=models.CASCADE,
        related_name='adventures',
        help_text="The dungeon master who owns this adventure"
    )
    
    name = models.CharField(
        max_length=255,
        help_text="Name of the adventure/campaign"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the adventure"
    )
    
    game_system = models.CharField(
        max_length=100,
        help_text="Game system (e.g., D&D 5e, Pathfinder, etc.)"
    )
    
    # Adventure settings and configuration
    adventure_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON configuration for adventure-specific settings"
    )
    
    world_building = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON data for world building elements (locations, NPCs, etc.)"
    )
    
    session_notes = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of session notes and summaries"
    )
    
    character_sheets = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of player character information"
    )
    
    campaign_timeline = models.JSONField(
        default=list,
        blank=True,
        help_text="Chronological events and timeline"
    )
    
    rules_modifications = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom rules and modifications for this adventure"
    )
    
    # Status and metadata
    status = models.CharField(
        max_length=20,
        choices=[
            ('planning', 'Planning'),
            ('active', 'Active'),
            ('paused', 'Paused'),
            ('completed', 'Completed'),
            ('archived', 'Archived')
        ],
        default='planning',
        help_text="Current status of the adventure"
    )
    
    is_public = models.BooleanField(
        default=False,
        help_text="Whether this adventure is publicly visible"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the adventure was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the adventure was last updated"
    )
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the adventure was started"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the adventure was completed"
    )
    
    # Game mechanics
    current_session = models.PositiveIntegerField(
        default=0,
        help_text="Current session number"
    )
    
    total_sessions = models.PositiveIntegerField(
        default=0,
        help_text="Total number of sessions played"
    )
    
    player_count = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Number of players in this adventure"
    )
    
    class Meta:
        db_table = 'adv_adventure'
        verbose_name = 'Adventure'
        verbose_name_plural = 'Adventures'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(player_count__gte=0, player_count__lte=10),
                name='valid_player_count'
            )
        ]
    
    def save(self, *args, **kwargs):
        """
        Override save to generate entity_id and validate adventure limit.
        """
        if not self.entity_id:
            # Generate 12-digit unique ID
            unique_id = str(uuid.uuid4().int)[:12]
            self.entity_id = f"adv-{unique_id}"
        
        # Validate that DM doesn't exceed 2 adventures limit
        if not self.pk:  # Only check on creation
            existing_count = Adventure.objects.filter(
                dungeon_master=self.dungeon_master
            ).count()
            if existing_count >= 2:
                raise ValueError("Dungeon Master can only have a maximum of 2 adventures")
        
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        """
        String representation showing adventure name and entity_id.
        """
        return f"{self.name} ({self.entity_id})"
    
    @property
    def dm_username(self) -> str:
        """
        Return the username of the dungeon master.
        """
        return self.dungeon_master.user.username
    
    @property
    def is_active(self) -> bool:
        """
        Check if the adventure is currently active.
        """
        return self.status == 'active'
    
    @property
    def session_count(self) -> int:
        """
        Return the number of sessions recorded.
        """
        return len(self.session_notes) if isinstance(self.session_notes, list) else 0
    
    def get_adventure_setting(self, key: str, default=None):
        """
        Get a specific adventure setting.
        
        Args:
            key: The setting key to retrieve
            default: Default value if key not found
            
        Returns:
            The setting value or default
        """
        return self.adventure_settings.get(key, default)
    
    def set_adventure_setting(self, key: str, value):
        """
        Set a specific adventure setting.
        
        Args:
            key: The setting key to set
            value: The value to set
        """
        self.adventure_settings[key] = value
        self.save()
    
    def add_session_note(self, note_data: dict):
        """
        Add a new session note.
        
        Args:
            note_data: Dictionary containing session note information
        """
        if not isinstance(self.session_notes, list):
            self.session_notes = []
        
        self.session_notes.append({
            'session_number': len(self.session_notes) + 1,
            'timestamp': str(timezone.now()),
            **note_data
        })
        self.total_sessions = len(self.session_notes)
        self.save()
    
    def update_status(self, new_status: str):
        """
        Update adventure status with appropriate timestamp handling.
        
        Args:
            new_status: New status to set
        """
        from django.utils import timezone
        
        old_status = self.status
        self.status = new_status
        
        if new_status == 'active' and old_status != 'active' and not self.started_at:
            self.started_at = timezone.now()
        elif new_status == 'completed' and old_status != 'completed':
            self.completed_at = timezone.now()
        
        self.save()
    
    def get_character_count(self) -> int:
        """
        Return the number of player characters.
        """
        return len(self.character_sheets) if isinstance(self.character_sheets, list) else 0 