import uuid
from django.db import models
from django.core.validators import MinValueValidator


class DSAAdvantage(models.Model):
    """
    DSA 4.1 Advantages System - Vorteile mit GP-Costs und Effects
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
    # Examples: "Glück", "Hohe Lebenskraft", "Verbesserte Regeneration"
    
    # Generation Point Cost (can be variable)
    gp_cost_base = models.IntegerField(validators=[MinValueValidator(0)])
    gp_cost_per_level = models.IntegerField(default=0, validators=[MinValueValidator(0)])  # For scalable advantages
    
    # Maximum levels (1 for binary advantages)
    max_levels = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Requirements (JSON)
    requirements = models.JSONField(default=dict)
    # Example: {"attributes": {"MU": 13}, "other_advantages": ["Magiedilettant"]}
    
    # Effects (JSON)
    effects = models.JSONField(default=dict)
    # Example: {"life_points": 7, "regeneration_bonus": 1}
    
    # Incompatible with (JSON list)
    incompatible_with = models.JSONField(default=list)
    # Example: ["Pech", "Niedrige Lebenskraft"]
    
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='general'
    )
    
    # Advantage-specific restrictions
    restrictions = models.JSONField(default=dict)
    # Example: {"max_levels_per_character": 1, "race_restrictions": ["Mensch"]}
    
    # Scaling effects (JSON)
    scaling_effects = models.JSONField(default=dict)
    # Example: {"life_points_per_level": 3, "regeneration_bonus_per_level": 1}
    
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'characters_dsa_advantage'
        verbose_name = 'DSA Advantage'
        verbose_name_plural = 'DSA Advantages'
    
    def __str__(self):
        return self.name
    
    def get_gp_cost(self, level=1):
        """Get GP cost for specific level"""
        return self.gp_cost_base + (self.gp_cost_per_level * (level - 1))
    
    def get_effect(self, effect_type, level=1):
        """Get effect value for specific type and level"""
        base_effect = self.effects.get(effect_type, 0)
        scaling_effect = self.scaling_effects.get(f"{effect_type}_per_level", 0)
        return base_effect + (scaling_effect * (level - 1))
    
    def get_requirement(self, requirement_type):
        """Get requirement for specific type"""
        return self.requirements.get(requirement_type)
    
    def is_incompatible_with(self, advantage_name):
        """Check if incompatible with specific advantage"""
        return advantage_name in self.incompatible_with
    
    def get_restriction(self, restriction_type):
        """Get advantage-specific restriction"""
        return self.restrictions.get(restriction_type)
    
    def check_requirements(self, character_data):
        """Check if character meets advantage requirements"""
        # Check attribute requirements
        attr_requirements = self.requirements.get('attributes', {})
        for attr, required_value in attr_requirements.items():
            if character_data.get('attributes', {}).get(attr, 0) < required_value:
                return False, f"Attribute {attr} below requirement ({required_value})"
        
        # Check other advantage requirements
        other_advantages = self.requirements.get('other_advantages', [])
        character_advantages = character_data.get('advantages', [])
        for required_advantage in other_advantages:
            if required_advantage not in character_advantages:
                return False, f"Required advantage '{required_advantage}' not found"
        
        return True, "All requirements met"
    
    def is_scalable(self):
        """Check if advantage is scalable (multiple levels)"""
        return self.max_levels > 1
    
    def get_total_gp_cost(self):
        """Get total GP cost for maximum levels"""
        if self.is_scalable():
            return sum(self.get_gp_cost(level) for level in range(1, self.max_levels + 1))
        return self.gp_cost_base 