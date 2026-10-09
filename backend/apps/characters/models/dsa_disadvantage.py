import uuid
from django.db import models
from django.core.validators import MinValueValidator


class DSADisadvantage(models.Model):
    """
    DSA 4.1 Disadvantages System - Nachteile mit GP-Gains und Effects
    """
    CATEGORY_CHOICES = [
        ('physical', 'Körperlich'),
        ('mental', 'Geistig'),
        ('social', 'Sozial'),
        ('supernatural', 'Übernatürlich'),
        ('general', 'Allgemein')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    # Examples: "Pech", "Niedrige Lebenskraft", "Aberglaube"
    
    # Generation Points gained (positive value)
    gp_gain_base = models.IntegerField(validators=[MinValueValidator(0)])
    gp_gain_per_level = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    max_levels = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Effects (JSON)
    effects = models.JSONField(default=dict)
    # Example: {"life_points": -7, "social_status": -1}
    
    # Incompatible with (JSON list)
    incompatible_with = models.JSONField(default=list)
    # Example: ["Glück", "Hohe Lebenskraft"]
    
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='general'
    )
    
    # Disadvantage-specific restrictions
    restrictions = models.JSONField(default=dict)
    # Example: {"max_levels_per_character": 1, "race_restrictions": ["Mensch"]}
    
    # Scaling effects (JSON)
    scaling_effects = models.JSONField(default=dict)
    # Example: {"life_points_per_level": -3, "social_status_per_level": -1}
    
    # Requirements (JSON) - some disadvantages might have requirements
    requirements = models.JSONField(default=dict)
    # Example: {"attributes": {"MU": 8}, "professions": ["Magier"]}
    
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'characters_dsa_disadvantage'
        verbose_name = 'DSA Disadvantage'
        verbose_name_plural = 'DSA Disadvantages'
    
    def __str__(self):
        return self.name
    
    def get_gp_gain(self, level=1):
        """Get GP gain for specific level"""
        return self.gp_gain_base + (self.gp_gain_per_level * (level - 1))
    
    def get_effect(self, effect_type, level=1):
        """Get effect value for specific type and level"""
        base_effect = self.effects.get(effect_type, 0)
        scaling_effect = self.scaling_effects.get(f"{effect_type}_per_level", 0)
        return base_effect + (scaling_effect * (level - 1))
    
    def is_incompatible_with(self, disadvantage_name):
        """Check if incompatible with specific disadvantage"""
        return disadvantage_name in self.incompatible_with
    
    def get_restriction(self, restriction_type):
        """Get disadvantage-specific restriction"""
        return self.restrictions.get(restriction_type)
    
    def get_requirement(self, requirement_type):
        """Get requirement for specific type"""
        return self.requirements.get(requirement_type)
    
    def check_requirements(self, character_data):
        """Check if character meets disadvantage requirements"""
        # Check attribute requirements
        attr_requirements = self.requirements.get('attributes', {})
        for attr, required_value in attr_requirements.items():
            if character_data.get('attributes', {}).get(attr, 0) > required_value:
                return False, f"Attribute {attr} above requirement ({required_value})"
        
        # Check profession requirements
        profession_requirements = self.requirements.get('professions', [])
        character_profession = character_data.get('profession')
        if profession_requirements and character_profession not in profession_requirements:
            return False, f"Profession '{character_profession}' not in required professions"
        
        return True, "All requirements met"
    
    def is_scalable(self):
        """Check if disadvantage is scalable (multiple levels)"""
        return self.max_levels > 1
    
    def get_total_gp_gain(self):
        """Get total GP gain for maximum levels"""
        if self.is_scalable():
            return sum(self.get_gp_gain(level) for level in range(1, self.max_levels + 1))
        return self.gp_gain_base 