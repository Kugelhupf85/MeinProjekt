from django.db import models
from .dsa_talent_base import DSATalentBase


class DSATalentCombat(DSATalentBase):
    """
    DSA 4.1 Combat Talents - Kampftalente
    """
    COMBAT_TYPE_CHOICES = [
        ('melee', 'Nahkampf'),
        ('ranged', 'Fernkampf'),
        ('shield', 'Schild'),
        ('armor', 'Rüstung'),
        ('tactical', 'Taktisch')
    ]
    
    combat_type = models.CharField(
        max_length=20,
        choices=COMBAT_TYPE_CHOICES,
        default='melee'
    )
    
    # Weapon categories this talent applies to (JSON)
    applicable_weapons = models.JSONField(default=list)
    # Example: ["Schwerter", "Säbel", "Anderthalbhänder"] for specific weapon talents
    
    # Combat-specific bonuses (JSON)
    combat_bonuses = models.JSONField(default=dict)
    # Example: {"attack_bonus": 1, "parry_bonus": 1, "damage_bonus": 1}
    
    # Special combat rules (JSON)
    combat_rules = models.JSONField(default=dict)
    # Example: {"can_parry_ranged": true, "special_attack_options": ["Finte"]}
    
    # Requirements for combat use (JSON)
    combat_requirements = models.JSONField(default=dict)
    # Example: {"weapon_requirements": ["Schwerter"], "armor_requirements": ["Leicht"]}
    
    class Meta:
        db_table = 'chr_dsa_talent_combat'
        verbose_name = 'DSA Combat Talent'
        verbose_name_plural = 'DSA Combat Talents'
    
    def __str__(self):
        return f"{self.name} ({self.get_combat_type_display()})"
    
    def is_applicable_to_weapon(self, weapon_name):
        """Check if talent is applicable to specific weapon"""
        return not self.applicable_weapons or weapon_name in self.applicable_weapons
    
    def get_combat_bonus(self, bonus_type):
        """Get specific combat bonus"""
        return self.combat_bonuses.get(bonus_type, 0)
    
    def get_combat_rule(self, rule_type):
        """Get specific combat rule"""
        return self.combat_rules.get(rule_type)
    
    def get_combat_requirement(self, requirement_type):
        """Get specific combat requirement"""
        return self.combat_requirements.get(requirement_type)
    
    def check_combat_requirements(self, character_data, weapon_data=None, armor_data=None):
        """Check if character meets combat-specific requirements"""
        # Check weapon requirements
        weapon_requirements = self.combat_requirements.get('weapon_requirements', [])
        if weapon_requirements and weapon_data:
            if weapon_data.get('category') not in weapon_requirements:
                return False, f"Weapon category '{weapon_data.get('category')}' not allowed"
        
        # Check armor requirements
        armor_requirements = self.combat_requirements.get('armor_requirements', [])
        if armor_requirements and armor_data:
            if armor_data.get('type') not in armor_requirements:
                return False, f"Armor type '{armor_data.get('type')}' not allowed"
        
        return True, "All combat requirements met" 