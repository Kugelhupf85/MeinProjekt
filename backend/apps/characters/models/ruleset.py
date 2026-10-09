import uuid
from django.db import models


class RuleSet(models.Model):
    """
    RuleSet Model for different game systems (DSA, D&D, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50, unique=True)
    # Examples: "dsa_4_1", "dungeons_and_dragons_5e", "pathfinder_2e"
    
    display_name = models.CharField(max_length=100)
    # Examples: "DSA 4.1", "D&D 5E", "Pathfinder 2E"
    
    version = models.CharField(max_length=20)
    
    # JSON Schema for validation of core_attributes
    attribute_schema = models.JSONField(default=dict)
    # Example: {"required": ["MU", "KL", "IN"], "properties": {"MU": {"type": "integer", "minimum": 8, "maximum": 20}}}
    
    # Default values for character creation
    default_values = models.JSONField(default=dict)
    # Example: {"generation_points_max": 110, "attribute_points_max": 100, "attribute_maximum": 14}
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'characters_ruleset'
        verbose_name = 'Rule Set'
        verbose_name_plural = 'Rule Sets'
    
    def __str__(self):
        return f"{self.display_name} ({self.version})"
    
    def get_attribute_schema(self):
        """Get the JSON schema for attribute validation"""
        return self.attribute_schema
    
    def get_default_values(self):
        """Get default values for character creation"""
        return self.default_values 