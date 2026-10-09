import uuid
from django.db import models


class DSARace(models.Model):
    """
    DSA 4.1 Race System - Rassen mit Attributs-Modifikatoren und Special Abilities
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50, unique=True)
    # Examples: "Mensch", "Elf", "Zwerg", "Halbling", "Ork"
    
    # Attribute Modifiers (JSON)
    attribute_modifiers = models.JSONField(default=dict)
    # Example: {"MU": 0, "KL": 1, "IN": 0, "CH": 0, "FF": 1, "GE": 0, "KO": -1, "KK": 0}
    
    # Special Abilities granted by race
    granted_special_abilities = models.JSONField(default=list)
    # Example: ["Infrared Vision", "Resistance to Magic"]
    
    # Starting modifications (JSON)
    starting_modifications = models.JSONField(default=dict)
    # Example: {"life_points": 5, "astral_energy": -5, "social_status": {"min": 1, "max": 6}}
    
    # Generation Point Cost
    generation_point_cost = models.IntegerField(default=0)
    
    # Race-specific restrictions
    restrictions = models.JSONField(default=dict)
    # Example: {"max_social_status": 6, "forbidden_professions": ["Geweihter"]}
    
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'characters_dsa_race'
        verbose_name = 'DSA Race'
        verbose_name_plural = 'DSA Races'
    
    def __str__(self):
        return self.name
    
    def get_attribute_modifier(self, attribute):
        """Get modifier for specific attribute"""
        return self.attribute_modifiers.get(attribute, 0)
    
    def get_starting_modification(self, key):
        """Get starting modification for specific key"""
        return self.starting_modifications.get(key, 0)
    
    def has_special_ability(self, ability_name):
        """Check if race grants specific special ability"""
        return ability_name in self.granted_special_abilities
    
    def get_restriction(self, restriction_type):
        """Get race-specific restriction"""
        return self.restrictions.get(restriction_type)
    
    def apply_to_attributes(self, base_attributes):
        """Apply race modifiers to base attributes"""
        modified_attributes = base_attributes.copy()
        for attr, modifier in self.attribute_modifiers.items():
            if attr in modified_attributes:
                modified_attributes[attr] += modifier
        return modified_attributes 