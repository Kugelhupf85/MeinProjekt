import uuid
from django.db import models
from django.core.validators import MinValueValidator


class DSASpecialAbilityTerrain(models.Model):
    """
    DSA 4.1 Terrain Knowledge Special Abilities System - Geländekunde Sonderfähigkeiten
    """
    TERRAIN_TYPE_CHOICES = [
        ('forest', 'Wald'),
        ('mountain', 'Gebirge'),
        ('desert', 'Wüste'),
        ('swamp', 'Sumpf'),
        ('city', 'Stadt'),
        ('village', 'Dorf'),
        ('coast', 'Küste'),
        ('underground', 'Untergrund'),
        ('arctic', 'Arktis'),
        ('jungle', 'Dschungel'),
        ('plains', 'Steppe'),
        ('island', 'Insel')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    # Examples: "Geländekunde (Wald)", "Geländekunde (Gebirge)", "Geländekunde (Stadt)"
    
    terrain_type = models.CharField(
        max_length=20,
        choices=TERRAIN_TYPE_CHOICES,
        default='forest'
    )
    
    # AP (Adventure Point) Cost
    ap_cost_base = models.IntegerField(default=3, validators=[MinValueValidator(0)])
    ap_cost_per_level = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    max_levels = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Bonuses granted in this terrain (JSON)
    terrain_bonuses = models.JSONField(default=dict)
    # Example: {"survival": 3, "tracking": 2, "stealth": 1, "orientation": 2}
    
    # Scaling bonuses (JSON)
    scaling_bonuses = models.JSONField(default=dict)
    # Example: {"survival_per_level": 1, "tracking_per_level": 1}
    
    # Requirements (JSON)
    requirements = models.JSONField(default=dict)
    # Example: {"attributes": {"IN": 12}, "talents": {"Wildnisleben": 8}}
    
    # Effects (JSON)
    effects = models.JSONField(default=dict)
    # Example: {"movement_bonus": 1, "encounter_reduction": 0.5}
    
    # Scaling effects (JSON)
    scaling_effects = models.JSONField(default=dict)
    # Example: {"movement_bonus_per_level": 1}
    
    # Incompatible with (JSON list)
    incompatible_with = models.JSONField(default=list)
    # Example: ["Geländekunde (Gebirge)", "Geländekunde (Wüste)"]
    
    # Terrain-specific restrictions
    restrictions = models.JSONField(default=dict)
    # Example: {"max_levels_per_character": 1, "race_restrictions": ["Mensch"]}
    
    # Prerequisites (JSON)
    prerequisites = models.JSONField(default=dict)
    # Example: {"talents": ["Wildnisleben"], "advantages": ["Gute Orientierung"]}
    
    # Terrain mechanics (JSON)
    terrain_mechanics = models.JSONField(default=dict)
    # Example: {"navigation_bonus": 2, "foraging_bonus": 1, "hiding_bonus": 1}
    
    # Special terrain features (JSON)
    special_features = models.JSONField(default=list)
    # Example: ["kennt_geheime_pfade", "kennt_wasserstellen", "kennt_gefährliche_gebiete"]
    
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chr_dsa_special_ability_terrain'
        verbose_name = 'DSA Terrain Special Ability'
        verbose_name_plural = 'DSA Terrain Special Abilities'
    
    def __str__(self):
        return f"{self.name} ({self.get_terrain_type_display()})"
    
    def get_ap_cost(self, level=1):
        """Get AP cost for specific level"""
        return self.ap_cost_base + (self.ap_cost_per_level * (level - 1))
    
    def get_terrain_bonus(self, bonus_type, level=1):
        """Get terrain bonus for specific type and level"""
        base_bonus = self.terrain_bonuses.get(bonus_type, 0)
        scaling_bonus = self.scaling_bonuses.get(f"{bonus_type}_per_level", 0)
        return base_bonus + (scaling_bonus * (level - 1))
    
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
    
    def get_terrain_mechanic(self, mechanic_type):
        """Get specific terrain mechanic"""
        return self.terrain_mechanics.get(mechanic_type)
    
    def has_special_feature(self, feature_name):
        """Check if ability grants specific terrain feature"""
        return feature_name in self.special_features
    
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
        
        # Check advantage requirements
        advantage_requirements = self.prerequisites.get('advantages', [])
        character_advantages = [ca.advantage.name for ca in character_data.get('character_advantages', [])]
        for advantage in advantage_requirements:
            if advantage not in character_advantages:
                return False, f"Missing advantage: {advantage}"
        
        return True, "All requirements met"
    
    def is_scalable(self):
        """Check if ability is scalable (multiple levels)"""
        return self.max_levels > 1
    
    def get_total_ap_cost(self):
        """Get total AP cost for maximum levels"""
        if self.is_scalable():
            return sum(self.get_ap_cost(level) for level in range(1, self.max_levels + 1))
        return self.ap_cost_base 