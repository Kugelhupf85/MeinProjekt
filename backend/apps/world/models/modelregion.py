"""
Region Model - Regional areas within worlds
"""

import uuid
from django.db import models
from .modelworld import World


class Region(models.Model):
    """
    Represents a region within a world.
    Regions are geographical/political areas that contain multiple locations.
    """
    
    # Primary identification
    entity_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Unique identifier with pattern RGN-{12_digit_id}"
    )
    
    # Relationship to world
    world = models.ForeignKey(
        World,
        on_delete=models.CASCADE,
        related_name='regions',
        help_text="The world this region belongs to"
    )
    
    # Basic region information
    name = models.CharField(
        max_length=200,
        help_text="Name of the region"
    )
    
    description = models.TextField(
        max_length=3000,
        help_text="Detailed region description"
    )
    
    # Atmosphere and characteristics
    general_mood = models.TextField(
        max_length=800,
        help_text="General atmosphere and mood of the region"
    )
    
    terrain_type = models.CharField(
        max_length=100,
        help_text="Primary terrain type (forest, mountains, plains, etc.)"
    )
    
    size_description = models.CharField(
        max_length=200,
        help_text="Description of the region's size and scope"
    )
    
    # Pill - Quick summary for fast access
    pill = models.JSONField(
        default=dict,
        blank=True,
        help_text="Quick summary containing all important information for fast access"
    )
    
    # Economic and cultural elements
    currencies = models.JSONField(
        default=list,
        help_text="Currencies used in this region"
    )
    
    important_personalities = models.JSONField(
        default=list,
        help_text="Key NPCs and important figures in the region"
    )
    
    religions = models.JSONField(
        default=list,
        help_text="Religious practices and beliefs in the region"
    )
    
    government_type = models.JSONField(
        default=dict,
        help_text="Government structure and political system"
    )
    
    cultural_traits = models.JSONField(
        default=list,
        help_text="Cultural characteristics and traditions"
    )
    
    # Settlements and infrastructure
    major_settlements = models.JSONField(
        default=list,
        help_text="Major cities, towns, and settlements"
    )
    
    natural_resources = models.JSONField(
        default=list,
        help_text="Natural resources and materials available"
    )
    
    trade_specialties = models.JSONField(
        default=list,
        help_text="Trade goods and economic specialties"
    )
    
    # Dangers and challenges
    threats_dangers = models.JSONField(
        default=list,
        help_text="Common threats, dangers, and challenges"
    )
    
    # Environmental factors
    climate_weather = models.JSONField(
        default=dict,
        help_text="Climate patterns and weather conditions"
    )
    
    # Social and legal systems
    laws_customs = models.JSONField(
        default=list,
        help_text="Local laws, customs, and social norms"
    )
    
    festivals_events = models.JSONField(
        default=list,
        help_text="Regular festivals, events, and celebrations"
    )
    
    # Military and defense
    military_forces = models.JSONField(
        default=list,
        help_text="Military forces, guards, and defense systems"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'wld_region_entity'
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'
        ordering = ['world__name', 'name']
        unique_together = ['world', 'name']
    
    def save(self, *args, **kwargs):
        """Generate entity_id if not present"""
        if not self.entity_id:
            # Generate 12-digit random number
            random_id = str(uuid.uuid4().int)[:12].zfill(12)
            self.entity_id = f"RGN-{random_id}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} in {self.world.name} ({self.entity_id})"
    
    @property
    def location_count(self):
        """Get the number of locations in this region"""
        return self.locations.count()
    
    def get_major_personalities(self):
        """Get list of major personalities with leadership roles"""
        return [p for p in self.important_personalities if p.get('role_importance', 0) >= 7]
    
    def get_primary_currency(self):
        """Get the primary currency used in this region"""
        if self.currencies:
            primary = next((c for c in self.currencies if c.get('is_primary', False)), None)
            return primary or self.currencies[0]
        return None
    
    def generate_pill(self):
        """Generate pill summary with key information"""
        if not self.pill:
            self.pill = {
                'entity_id': self.entity_id,
                'name': self.name,
                'world_name': self.world.name,
                'world_entity_id': self.world.entity_id,
                'description_preview': self.description[:150] + '...' if len(self.description) > 150 else self.description,
                'general_mood': self.general_mood,
                'terrain_type': self.terrain_type,
                'size_description': self.size_description,
                'location_count': self.location_count,
                'primary_currency': self.get_primary_currency(),
                'government_type': self.government_type.get('type', 'Unknown') if self.government_type else 'Unknown',
                'major_personalities': [p.get('name', 'Unknown') for p in self.get_major_personalities()[:3]],
                'key_settlements': [s.get('name', 'Unknown') for s in self.major_settlements[:3]] if self.major_settlements else [],
                'primary_threats': [t.get('name', 'Unknown') for t in self.threats_dangers[:3]] if self.threats_dangers else [],
                'trade_specialties': [t.get('name', 'Unknown') for t in self.trade_specialties[:3]] if self.trade_specialties else [],
                'climate_type': self.climate_weather.get('type', 'Unknown') if self.climate_weather else 'Unknown',
                'generated_at': self.updated_at.isoformat() if self.updated_at else None,
                'is_active': self.is_active
            }
            self.save(update_fields=['pill'])
        return self.pill
    
    def refresh_pill(self):
        """Force refresh of pill summary"""
        self.pill = {}
        return self.generate_pill() 