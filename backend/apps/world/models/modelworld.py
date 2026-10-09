"""
World Model - Pen & Paper World Management
"""

import uuid
from django.db import models
from django.core.validators import MaxLengthValidator
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class World(models.Model):
    """
    Represents a complete fantasy world for pen & paper adventures.
    Contains all essential worldbuilding elements for consistent storytelling.
    """
    
    # Primary identification
    entity_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Unique identifier with pattern WLD-{12_digit_id}"
    )
    
    # Basic world information
    name = models.CharField(
        max_length=200,
        help_text="Name of the world"
    )
    
    description = models.TextField(
        max_length=5000,
        help_text="Detailed world description (max 5000 characters)"
    )
    
    # Atmosphere and mood
    general_mood = models.TextField(
        max_length=1000,
        help_text="General atmosphere and mood of the world"
    )
    
    # Pill - Quick summary for fast access
    pill = models.JSONField(
        default=dict,
        blank=True,
        help_text="Quick summary containing all important information for fast access"
    )
    
    # Important locations as JSON
    important_locations = models.JSONField(
        default=list,
        help_text="List of important world locations with descriptions"
    )
    
    # World conventions and rules
    conventions = models.JSONField(
        default=dict,
        help_text="Important world conventions, laws, and social rules"
    )
    
    # Time system
    time_system = models.JSONField(
        default=dict,
        help_text="Custom time system (calendar, months, days, hours)"
    )
    
    # Current world date
    current_date = models.CharField(
        max_length=100,
        help_text="Current date in the world's time system"
    )
    
    # Measurement systems
    measurement_units = models.JSONField(
        default=dict,
        help_text="Custom measurement units (distance, weight, currency)"
    )
    
    # Religious systems
    religions = models.JSONField(
        default=list,
        help_text="Religious systems, pantheons, and belief structures"
    )
    
    # Extended worldbuilding elements
    magic_system = models.JSONField(
        default=dict,
        help_text="Magic system rules, limitations, and mechanics"
    )
    
    political_systems = models.JSONField(
        default=list,
        help_text="Political structures, governments, and power dynamics"
    )
    
    languages = models.JSONField(
        default=list,
        help_text="Languages spoken in the world with cultural context"
    )
    
    history_timeline = models.JSONField(
        default=list,
        help_text="Major historical events and timeline"
    )
    
    climate_zones = models.JSONField(
        default=list,
        help_text="Climate zones and weather patterns"
    )
    
    natural_phenomena = models.JSONField(
        default=list,
        help_text="Unique natural phenomena and environmental features"
    )
    
    trade_routes = models.JSONField(
        default=list,
        help_text="Major trade routes and economic connections"
    )
    
    conflicts_tensions = models.JSONField(
        default=list,
        help_text="Current conflicts, tensions, and plot hooks"
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_worlds',
        help_text="User who created this world"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'wld_world_entity'
        verbose_name = 'World'
        verbose_name_plural = 'Worlds'
        ordering = ['name']
        
    def save(self, *args, **kwargs):
        """
        Override save to generate entity_id if not present.
        """
        if not self.entity_id:
            # Generate 12-digit unique ID
            unique_id = str(uuid.uuid4().int)[:12]
            self.entity_id = f"WLD-{unique_id}"
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.name} ({self.entity_id})"
    
    @property
    def region_count(self) -> int:
        """Return the number of regions in this world."""
        return self.regions.filter(is_active=True).count()
    
    @property
    def total_locations(self) -> int:
        """Return the total number of locations in this world."""
        total = 0
        for region in self.regions.filter(is_active=True):
            total += region.locations.filter(is_active=True).count()
        return total
    
    def generate_pill(self):
        """Generate pill summary with key information"""
        if not self.pill:
            self.pill = {
                'entity_id': self.entity_id,
                'name': self.name,
                'description_preview': self.description[:200] + '...' if len(self.description) > 200 else self.description,
                'general_mood': self.general_mood,
                'current_date': self.current_date,
                'region_count': self.region_count,
                'total_locations': self.total_locations,
                'key_religions': [r.get('name', 'Unknown') for r in self.religions[:3]] if self.religions else [],
                'primary_languages': [l.get('name', 'Unknown') for l in self.languages[:3]] if self.languages else [],
                'magic_system_type': self.magic_system.get('type', 'Unknown') if self.magic_system else 'Unknown',
                'major_conflicts': [c.get('name', 'Unknown') for c in self.conflicts_tensions[:3]] if self.conflicts_tensions else [],
                'climate_summary': [c.get('name', 'Unknown') for c in self.climate_zones[:3]] if self.climate_zones else [],
                'generated_at': self.updated_at.isoformat() if self.updated_at else None,
                'is_active': self.is_active
            }
            self.save(update_fields=['pill'])
        return self.pill
    
    def refresh_pill(self):
        """Force refresh of pill summary"""
        self.pill = {}
        return self.generate_pill()


class WorldAPIKeys(models.Model):
    """
    World API Keys model for encrypted storage of external service API keys.
    
    This model stores API keys per world, allowing different worlds to use
    different AI providers and configurations.
    """
    
    KEY_STATUS_CHOICES = [
        ('not_configured', 'Not Configured'),
        ('configured', 'Configured'),
        ('invalid', 'Invalid'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
    ]
    
    world = models.OneToOneField(
        World,
        on_delete=models.CASCADE,
        related_name='api_keys',
        help_text="Link to World"
    )
    
    # Encrypted API Keys (using pgcrypto extension)
    openai_key_encrypted = models.BinaryField(
        null=True,
        blank=True,
        help_text="Encrypted OpenAI API key"
    )
    
    anthropic_key_encrypted = models.BinaryField(
        null=True,
        blank=True,
        help_text="Encrypted Anthropic API key"
    )
    
    google_key_encrypted = models.BinaryField(
        null=True,
        blank=True,
        help_text="Encrypted Google API key"
    )
    
    deepseek_key_encrypted = models.BinaryField(
        null=True,
        blank=True,
        help_text="Encrypted DeepSeek API key"
    )
    
    # Key Status and Metadata
    openai_status = models.CharField(
        max_length=20,
        choices=KEY_STATUS_CHOICES,
        default='not_configured',
        help_text="Status of the OpenAI API key"
    )
    
    anthropic_status = models.CharField(
        max_length=20,
        choices=KEY_STATUS_CHOICES,
        default='not_configured',
        help_text="Status of the Anthropic API key"
    )
    
    google_status = models.CharField(
        max_length=20,
        choices=KEY_STATUS_CHOICES,
        default='not_configured',
        help_text="Status of the Google API key"
    )
    
    deepseek_status = models.CharField(
        max_length=20,
        choices=KEY_STATUS_CHOICES,
        default='not_configured',
        help_text="Status of the DeepSeek API key"
    )
    
    # Last Validation Timestamps
    openai_last_validated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time the OpenAI key was validated"
    )
    
    anthropic_last_validated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time the Anthropic key was validated"
    )
    
    google_last_validated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time the Google key was validated"
    )
    
    deepseek_last_validated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time the DeepSeek key was validated"
    )
    
    # Usage Tracking (for rate limiting and monitoring)
    usage_statistics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Usage statistics for rate limiting and monitoring"
    )
    
    # Security Metadata
    encryption_version = models.IntegerField(
        default=1,
        help_text="Encryption version for key rotation"
    )
    
    last_key_update = models.DateTimeField(
        auto_now=True,
        help_text="Last time any key was updated"
    )
    
    security_notes = models.TextField(
        blank=True,
        help_text="Admin notes about key issues"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the keys were created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the keys were last updated"
    )
    
    class Meta:
        db_table = 'wld_world_api_keys'
        verbose_name = 'World API Keys'
        verbose_name_plural = 'World API Keys'
        ordering = ['-updated_at']
        
    def __str__(self) -> str:
        return f"API Keys for {self.world.name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to set default usage statistics if not present.
        """
        if not self.usage_statistics:
            self.usage_statistics = {
                "openai": {"requests_today": 0, "last_request": None},
                "anthropic": {"requests_today": 0, "last_request": None},
                "google": {"requests_today": 0, "last_request": None},
                "deepseek": {"requests_today": 0, "last_request": None}
            }
        super().save(*args, **kwargs)
    
    def get_configured_providers(self):
        """Get list of configured API providers."""
        providers = []
        if self.openai_status == 'configured':
            providers.append('openai')
        if self.anthropic_status == 'configured':
            providers.append('anthropic')
        if self.google_status == 'configured':
            providers.append('google')
        if self.deepseek_status == 'configured':
            providers.append('deepseek')
        return providers
    
    def is_provider_configured(self, provider: str) -> bool:
        """Check if a specific provider is configured."""
        return getattr(self, f"{provider}_status", None) == 'configured'
    
    def mark_provider_invalid(self, provider: str):
        """Mark a provider's key as invalid."""
        if hasattr(self, f"{provider}_status"):
            setattr(self, f"{provider}_status", 'invalid')
            self.save()
    
    def mark_provider_configured(self, provider: str):
        """Mark a provider's key as configured."""
        if hasattr(self, f"{provider}_status"):
            setattr(self, f"{provider}_status", 'configured')
            setattr(self, f"{provider}_last_validated", timezone.now())
            self.save()
    
    def increment_usage(self, provider: str):
        """Increment usage counter for a provider."""
        if provider in self.usage_statistics:
            self.usage_statistics[provider]["requests_today"] += 1
            self.usage_statistics[provider]["last_request"] = timezone.now().isoformat()
            self.save()
    
    def reset_daily_usage(self):
        """Reset daily usage counters for all providers."""
        for provider in self.usage_statistics:
            self.usage_statistics[provider]["requests_today"] = 0
        self.save()


class WorldParty(models.Model):
    """
    A party represents a group of users who play together in a specific world.
    Each world has one party, and the party is world-specific.
    """
    
    entity_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Unique entity identifier with format: WP-{12_digit_id}"
    )
    
    world = models.OneToOneField(
        World,
        on_delete=models.CASCADE,
        related_name='party',
        help_text="The world this party belongs to"
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Name of the party"
    )
    
    description = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Description of the party"
    )
    
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_world_parties',
        help_text="User who created this party"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this party is active"
    )
    
    is_public = models.BooleanField(
        default=False,
        help_text="Can others discover this party?"
    )
    
    max_members = models.IntegerField(
        default=8,
        help_text="Maximum party size"
    )
    
    # Party Configuration
    party_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Party-specific settings and configuration"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the party was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the party was last updated"
    )
    
    class Meta:
        db_table = 'wld_world_party'
        verbose_name = 'World Party'
        verbose_name_plural = 'World Parties'
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        """
        Override save to generate entity_id if not present.
        """
        if not self.entity_id:
            # Generate 12-digit unique ID
            unique_id = str(uuid.uuid4().int)[:12]
            self.entity_id = f"WP-{unique_id}"
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.name} ({self.entity_id}) - {self.world.name}"
    
    @property
    def member_count(self) -> int:
        """Return the number of active members in this party."""
        return self.memberships.filter(status='active').count()
    
    @property
    def is_full(self) -> bool:
        """Check if party has reached maximum capacity."""
        return self.member_count >= self.max_members
    
    def get_dungeon_masters(self):
        """Get all users with dungeon_master role in this party."""
        return self.memberships.filter(
            role='dungeon_master',
            status='active'
        ).select_related('user')
    
    def get_players(self):
        """Get all users with player role in this party."""
        return self.memberships.filter(
            role='player',
            status='active'
        ).select_related('user')
    
    def get_active_members(self):
        """Get all active members regardless of role."""
        return self.memberships.filter(
            status='active'
        ).select_related('user')
    
    def get_active_dm(self):
        """Get the currently active dungeon master."""
        return self.memberships.filter(
            role='dungeon_master',
            status='active'
        ).first()


class WorldPartyMembership(models.Model):
    """
    Defines the relationship between users and world parties.
    Tracks roles, permissions, and membership status.
    """
    
    ROLE_CHOICES = [
        ('player', 'Player'),
        ('dungeon_master', 'Dungeon Master'),
        ('co_dm', 'Co-Dungeon Master'),
        ('observer', 'Observer'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('invited', 'Invited'),
        ('banned', 'Banned'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='world_party_memberships',
        help_text="User who is a member of the party"
    )
    
    party = models.ForeignKey(
        WorldParty,
        on_delete=models.CASCADE,
        related_name='memberships',
        help_text="Party that the user is a member of"
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='player',
        help_text="Role of the user in this party"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='invited',
        help_text="Status of the membership"
    )
    
    # Permissions
    can_invite_members = models.BooleanField(
        default=False,
        help_text="Can invite new members to the party"
    )
    
    can_manage_campaigns = models.BooleanField(
        default=False,
        help_text="Can create and manage campaigns"
    )
    
    can_edit_party = models.BooleanField(
        default=False,
        help_text="Can edit party details"
    )
    
    can_change_roles = models.BooleanField(
        default=False,
        help_text="Can change other members' roles"
    )
    
    can_remove_members = models.BooleanField(
        default=False,
        help_text="Can remove other members from the party"
    )
    
    can_access_api_keys = models.BooleanField(
        default=False,
        help_text="Can access and use world API keys"
    )
    
    joined_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the user joined the party"
    )
    
    last_active = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the user was last active in the party"
    )
    
    class Meta:
        db_table = 'wld_world_party_membership'
        verbose_name = 'World Party Membership'
        verbose_name_plural = 'World Party Memberships'
        unique_together = ['user', 'party']
        ordering = ['-joined_at']
        
    def __str__(self) -> str:
        return f"{self.user.email} - {self.party.name} ({self.role})"
    
    def save(self, *args, **kwargs):
        """
        Override save to set default permissions based on role.
        """
        if self.role == 'dungeon_master':
            # DMs get most permissions by default
            self.can_invite_members = True
            self.can_manage_campaigns = True
            self.can_edit_party = True
            self.can_change_roles = True
            self.can_remove_members = True
            self.can_access_api_keys = True
        elif self.role == 'co_dm':
            # Co-DMs get campaign management permissions
            self.can_manage_campaigns = True
            self.can_invite_members = True
            self.can_access_api_keys = True
        elif self.role == 'player':
            # Players get basic permissions
            self.can_invite_members = False
            self.can_manage_campaigns = False
            self.can_edit_party = False
            self.can_change_roles = False
            self.can_remove_members = False
            self.can_access_api_keys = False
        elif self.role == 'observer':
            # Observers get no permissions
            self.can_invite_members = False
            self.can_manage_campaigns = False
            self.can_edit_party = False
            self.can_change_roles = False
            self.can_remove_members = False
            self.can_access_api_keys = False
        
        super().save(*args, **kwargs)
    
    def promote_to_dm(self):
        """Promote this member to dungeon master role."""
        self.role = 'dungeon_master'
        self.save()
    
    def demote_to_player(self):
        """Demote this member to player role."""
        self.role = 'player'
        self.save()
    
    def make_co_dm(self):
        """Make this member a co-dungeon master."""
        self.role = 'co_dm'
        self.save()
    
    def activate(self):
        """Activate this membership (accept invitation)."""
        self.status = 'active'
        self.save()
    
    def deactivate(self):
        """Deactivate this membership."""
        self.status = 'inactive'
        self.save()
    
    def ban(self):
        """Ban this member from the party."""
        self.status = 'banned'
        self.save() 