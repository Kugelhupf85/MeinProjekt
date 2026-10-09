import uuid
from django.db import models
from django.core.validators import MinValueValidator


class DSASpecialAbilityCombat(models.Model):
    """
    DSA 4.1 Combat Special Abilities System - Kampfsonderfähigkeiten
    """
    COMBAT_TYPE_CHOICES = [
        ('melee', 'Nahkampf'),
        ('ranged', 'Fernkampf'), 
        ('maneuver', 'Manöver'),
        ('defense', 'Verteidigung'),
        ('tactical', 'Taktisch')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    # Examples: "Wuchtschlag", "Finte", "Riposte", "Schildwall"
    
    combat_type = models.CharField(
        max_length=20,
        choices=COMBAT_TYPE_CHOICES,
        default='melee'
    )
    
    # AP (Adventure Point) Cost
    ap_cost_base = models.IntegerField(validators=[MinValueValidator(0)])
    ap_cost_per_level = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    max_levels = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Weapon/Combat restrictions (JSON)
    applicable_weapons = models.JSONField(default=list)
    # Example: ["Schwerter", "Säbel", "Anderthalbhänder"] for specific maneuvers
    
    # Combat situation restrictions (JSON)
    combat_situations = models.JSONField(default=list)
    # Example: ["nur_gegen_nahkampfwaffen", "nur_bei_verteidigung", "nur_bei_angriff"]
    
    # Requirements (JSON)
    requirements = models.JSONField(default=dict)
    # Example: {"attributes": {"GE": 13, "KK": 15}, "talents": {"Schwerter": 10}, "special_abilities": ["Kampfreflexe"]}
    
    # Effects (JSON)
    effects = models.JSONField(default=dict)
    # Example: {"attack_bonus": 2, "damage_bonus": 1, "parry_bonus": 1}
    
    # Scaling effects (JSON)
    scaling_effects = models.JSONField(default=dict)
    # Example: {"attack_bonus_per_level": 1, "damage_bonus_per_level": 1}
    
    # Incompatible with (JSON list)
    incompatible_with = models.JSONField(default=list)
    # Example: ["Schildkampf", "Zweihandkampf"]
    
    # Combat-specific restrictions
    restrictions = models.JSONField(default=dict)
    # Example: {"max_levels_per_character": 1, "weapon_restrictions": ["nur_einhändig"]}
    
    # Prerequisites (JSON)
    prerequisites = models.JSONField(default=dict)
    # Example: {"advantages": ["Kampfreflexe"], "professions": ["Krieger"]}
    
    # Combat mechanics (JSON)
    combat_mechanics = models.JSONField(default=dict)
    # Example: {"action_type": "reaktion", "trigger": "bei_angriff", "cost": "1_aktion"}
    
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chr_dsa_special_ability_combat'
        verbose_name = 'DSA Combat Special Ability'
        verbose_name_plural = 'DSA Combat Special Abilities'
    
    def __str__(self):
        return f"{self.name} ({self.get_combat_type_display()})"
    
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
    
    def is_applicable_to_weapon(self, weapon_name):
        """Check if ability is applicable to specific weapon"""
        return not self.applicable_weapons or weapon_name in self.applicable_weapons
    
    def is_applicable_in_situation(self, situation):
        """Check if ability is applicable in specific combat situation"""
        return not self.combat_situations or situation in self.combat_situations
    
    def get_combat_mechanic(self, mechanic_type):
        """Get specific combat mechanic"""
        return self.combat_mechanics.get(mechanic_type)
    
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