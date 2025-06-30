"""
Location Model - Specific locations within regions
"""

import uuid
from django.db import models
from .modelregion import Region


class Location(models.Model):
    """
    Represents a specific location within a region.
    Locations are the smallest geographical units in the world hierarchy.
    """
    
    # Location type choices
    LOCATION_TYPES = [
        ('city', 'City'),
        ('town', 'Town'),
        ('village', 'Village'),
        ('dungeon', 'Dungeon'),
        ('ruins', 'Ruins'),
        ('temple', 'Temple'),
        ('castle', 'Castle'),
        ('forest', 'Forest'),
        ('mountain', 'Mountain'),
        ('cave', 'Cave'),
        ('tavern', 'Tavern'),
        ('shop', 'Shop'),
        ('landmark', 'Landmark'),
        ('other', 'Other'),
    ]
    
    # Primary identification
    entity_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Unique identifier with pattern LOC-{12_digit_id}"
    )
    
    # Relationship to region
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='locations',
        help_text="The region this location belongs to"
    )
    
    # Basic location information
    name = models.CharField(
        max_length=200,
        help_text="Name of the location"
    )
    
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPES,
        default='other',
        help_text="Type of location"
    )
    
    description = models.TextField(
        max_length=2000,
        help_text="Detailed location description"
    )
    
    # Atmosphere and characteristics
    general_mood = models.TextField(
        max_length=600,
        help_text="General atmosphere and mood of the location"
    )
    
    size_scale = models.CharField(
        max_length=100,
        help_text="Size scale description (tiny, small, medium, large, massive)"
    )
    
    accessibility = models.CharField(
        max_length=200,
        help_text="How accessible the location is (roads, paths, hidden, etc.)"
    )
    
    # Pill - Quick summary for fast access
    pill = models.JSONField(
        default=dict,
        blank=True,
        help_text="Quick summary containing all important information for fast access"
    )
    
    # Characters and NPCs
    important_personalities = models.JSONField(
        default=list,
        help_text="Key NPCs and important figures at this location"
    )
    
    # Services and facilities
    services_available = models.JSONField(
        default=list,
        help_text="Services, shops, and facilities available"
    )
    
    # Physical characteristics
    notable_features = models.JSONField(
        default=list,
        help_text="Notable physical features and landmarks"
    )
    
    # Secrets and mysteries
    secrets_hidden = models.JSONField(
        default=list,
        help_text="Hidden secrets, mysteries, and concealed information"
    )
    
    # Adventure elements
    encounters_possible = models.JSONField(
        default=list,
        help_text="Possible encounters, events, and interactions"
    )
    
    items_treasures = models.JSONField(
        default=list,
        help_text="Items, treasures, and valuable objects"
    )
    
    # Security and defenses
    defenses_security = models.JSONField(
        default=list,
        help_text="Defensive measures, guards, and security systems"
    )
    
    # Demographics and society
    population_demographics = models.JSONField(
        default=dict,
        help_text="Population size, demographics, and social structure"
    )
    
    economic_activity = models.JSONField(
        default=list,
        help_text="Economic activities, trade, and commerce"
    )
    
    # Travel and connections
    connections_travel = models.JSONField(
        default=list,
        help_text="Travel connections, roads, and transportation"
    )
    
    # Information and rumors
    rumors_information = models.JSONField(
        default=list,
        help_text="Local rumors, gossip, and information sources"
    )
    
    # Dynamic elements
    seasonal_changes = models.JSONField(
        default=list,
        help_text="How the location changes with seasons or time"
    )
    
    current_events = models.JSONField(
        default=list,
        help_text="Current events and ongoing situations"
    )
    
    # Quest and adventure hooks
    quest_opportunities = models.JSONField(
        default=list,
        help_text="Quest hooks, adventure opportunities, and plot threads"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'wld_location_entity'
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        ordering = ['region__world__name', 'region__name', 'name']
        unique_together = ['region', 'name']
    
    def save(self, *args, **kwargs):
        """Generate entity_id if not present"""
        if not self.entity_id:
            # Generate 12-digit random number
            random_id = str(uuid.uuid4().int)[:12].zfill(12)
            self.entity_id = f"LOC-{random_id}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.get_location_type_display()}) in {self.region.name} ({self.entity_id})"
    
    @property
    def world(self):
        """Get the world this location belongs to"""
        return self.region.world
    
    @property
    def full_path(self):
        """Get the full hierarchical path: World > Region > Location"""
        return f"{self.world.name} > {self.region.name} > {self.name}"
    
    def get_key_npcs(self):
        """Get list of key NPCs with high importance"""
        return [p for p in self.important_personalities if p.get('importance', 0) >= 7]
    
    def get_available_services(self):
        """Get list of available services for quick reference"""
        return [s for s in self.services_available if s.get('available', True)]
    
    def get_current_plot_hooks(self):
        """Get current active plot hooks and quest opportunities"""
        active_quests = [q for q in self.quest_opportunities if q.get('active', True)]
        current_events = [e for e in self.current_events if e.get('ongoing', True)]
        return active_quests + current_events
    
    def generate_pill(self):
        """Generate pill summary with key information"""
        if not self.pill:
            self.pill = {
                'entity_id': self.entity_id,
                'name': self.name,
                'location_type': self.location_type,
                'location_type_display': self.get_location_type_display(),
                'region_name': self.region.name,
                'region_entity_id': self.region.entity_id,
                'world_name': self.world.name,
                'world_entity_id': self.world.entity_id,
                'full_path': self.full_path,
                'description_preview': self.description[:120] + '...' if len(self.description) > 120 else self.description,
                'general_mood': self.general_mood,
                'size_scale': self.size_scale,
                'accessibility': self.accessibility,
                'key_npcs': [p.get('name', 'Unknown') for p in self.get_key_npcs()[:3]],
                'available_services': [s.get('name', 'Unknown') for s in self.get_available_services()[:3]],
                'notable_features': [f.get('name', 'Unknown') for f in self.notable_features[:3]] if self.notable_features else [],
                'active_plot_hooks': len(self.get_current_plot_hooks()),
                'population_size': self.population_demographics.get('size', 'Unknown') if self.population_demographics else 'Unknown',
                'security_level': self.defenses_security[0].get('level', 'Unknown') if self.defenses_security else 'Unknown',
                'primary_activity': self.economic_activity[0].get('type', 'Unknown') if self.economic_activity else 'Unknown',
                'generated_at': self.updated_at.isoformat() if self.updated_at else None,
                'is_active': self.is_active
            }
            self.save(update_fields=['pill'])
        return self.pill
    
    def refresh_pill(self):
        """Force refresh of pill summary"""
        self.pill = {}
        return self.generate_pill() 