"""
World Model - Pen & Paper World Management
"""

import uuid
from django.db import models
from django.core.validators import MaxLengthValidator


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'wld_world_entity'
        verbose_name = 'World'
        verbose_name_plural = 'Worlds'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        """Generate entity_id if not present"""
        if not self.entity_id:
            # Generate 12-digit random number
            random_id = str(uuid.uuid4().int)[:12].zfill(12)
            self.entity_id = f"WLD-{random_id}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.entity_id})"
    
    @property
    def region_count(self):
        """Get the number of regions in this world"""
        return self.regions.count()
    
    @property
    def total_locations(self):
        """Get total number of locations across all regions"""
        return sum(region.location_count for region in self.regions.all())
    
    def get_active_adventures(self):
        """Get all active adventures using this world"""
        from apps.adventure.models import Adventure
        return Adventure.objects.filter(world=self, is_active=True)
    
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