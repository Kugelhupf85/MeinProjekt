import uuid
from django.db import models
from django.core.validators import MinValueValidator


class DSASpecialAbilityGeneral(models.Model):
    """
    DSA 4.1 General Special Abilities System - Allgemeine Sonderfähigkeiten
    """
    CATEGORY_CHOICES = [
        ('combat', 'Kampf'),
        ('movement', 'Bewegung'),
        ('social', 'Sozial'),
        ('survival', 'Überleben'),
        ('magic', 'Magisch'),
        ('general', 'Allgemein')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    # Examples: "Kampfreflexe", "Wuchtschlag", "Berittener Kampf", "Zweikampf"
    
    # AP (Adventure Point) Cost
    ap_cost_base = models.IntegerField(validators=[MinValueValidator(0)])
    ap_cost_per_level = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    max_levels = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general'
    )
    
    # Requirements (JSON)
    requirements = models.JSONField(default=dict)
    # Example: {"attributes": {"GE": 13, "KK": 15}, "talents": {"Schwerter": 10}, "special_abilities": ["Kampfreflexe"]}
    
    # Effects (JSON)
    effects = models.JSONField(default=dict)
    # Example: {"attack_bonus": 2, "damage_bonus": 1, "initiative_bonus": 1}
    
    # Scaling effects (JSON)
    scaling_effects = models.JSONField(default=dict)
    # Example: {"attack_bonus_per_level": 1, "damage_bonus_per_level": 1}
    
    # Incompatible with (JSON list)
    incompatible_with = models.JSONField(default=list)
    # Example: ["Schildkampf", "Zweihandkampf"]
    
    # Special ability-specific restrictions
    restrictions = models.JSONField(default=dict)
    # Example: {"max_levels_per_character": 1, "race_restrictions": ["Mensch"]}
    
    # Prerequisites (JSON)
    prerequisites = models.JSONField(default=dict)
    # Example: {"advantages": ["Kampfreflexe"], "professions": ["Krieger"]}
    
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chr_dsa_special_ability_general'
        verbose_name = 'DSA General Special Ability'
        verbose_name_plural = 'DSA General Special Abilities'
    
    def __str__(self):
        return self.name
    
    def get_ap_cost(self, level=1):
        """Get AP cost for specific level"""
        return self.ap_cost_base + (self.ap_cost_per_level * (level - 1))
    
    def get_effect(self, effect_type, level=1):
        """Get effect value for specific type and level"""
        base_effect = self.effects.get(effect_type, 0)
        scaling_effect = self.scaling_effects.get(f"{effect_type}_per_level", 0)
        return base_effect + (scaling_effect * (level - 1))
    
    def get_requirement(self, requirement_type):
        """Get requirement for specific type"""
        return self.requirements.get(requirement_type)
    
    def is_incompatible_with(self, ability_name):
        """Check if incompatible with specific ability"""
        return ability_name in self.incompatible_with
    
    def get_restriction(self, restriction_type):
        """Get ability-specific restriction"""
        return self.restrictions.get(restriction_type)
    
    def get_prerequisite(self, prerequisite_type):
        """Get prerequisite for specific type"""
        return self.prerequisites.get(prerequisite_type)
    
    def check_requirements(self, character_data):
        """Check if character meets ability requirements"""
        # Check attribute requirements
        attr_requirements = self.requirements.get('attributes', {})
        for attr, required_value in attr_requirements.items():
            if character_data.get('attributes', {}).get(attr, 0) < required_value:
                return False, f"Attribute {attr} below requirement ({required_value})"
        
        # Check talent requirements
        talent_requirements = self.requirements.get('talents', {})
        for talent, required_value in talent_requirements.items():
            if character_data.get('talents', {}).get(talent, 0) < required_value:
                return False, f"Talent {talent} below requirement ({required_value})"
        
        # Check special ability requirements
        ability_requirements = self.requirements.get('special_abilities', [])
        character_abilities = character_data.get('special_abilities', [])
        for ability in ability_requirements:
            if ability not in character_abilities:
                return False, f"Missing special ability: {ability}"
        
        return True, "All requirements met"
    
    def is_scalable(self):
        """Check if ability is scalable (multiple levels)"""
        return self.max_levels > 1
    
    def get_total_ap_cost(self):
        """Get total AP cost for maximum levels"""
        if self.is_scalable():
            return sum(self.get_ap_cost(level) for level in range(1, self.max_levels + 1))
        return self.ap_cost_base 