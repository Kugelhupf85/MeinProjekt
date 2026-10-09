import uuid
from django.db import models


class DSAProfession(models.Model):
    """
    DSA 4.1 Profession System - Professionen mit Requirements und Starting Equipment
    """
    CATEGORY_CHOICES = [
        ('mundane', 'Mundane'),
        ('magic', 'Magic User'), 
        ('clerical', 'Blessed One'),
        ('combat', 'Fighter')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50, unique=True)
    # Examples: "Krieger", "Magier", "Geweihter", "Streuner", "Handwerker"
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='mundane'
    )
    
    # Attribute Requirements (JSON)
    attribute_requirements = models.JSONField(default=dict)
    # Example: {"MU": 13, "KL": 11, "IN": 12} for Magier
    
    # Talent Bonuses (JSON)
    talent_bonuses = models.JSONField(default=dict)
    # Example: {"Schwerter": 5, "Raufen": 3, "Körperbeherrschung": 4}
    
    # Special Abilities granted (JSON)
    granted_special_abilities = models.JSONField(default=list)
    # Example: ["Kampfreflexe", "Wuchtschlag"] for Krieger
    
    # Starting Equipment (JSON)
    starting_equipment = models.JSONField(default=dict)
    # Example: {"weapons": ["Schwert", "Schild"], "armor": ["Lederrüstung"], "money": 150}
    
    # Generation Point Cost
    generation_point_cost = models.IntegerField(default=0)
    
    # Profession-specific restrictions
    restrictions = models.JSONField(default=dict)
    # Example: {"forbidden_advantages": ["Magiedilettant"], "required_races": ["Mensch"]}
    
    # Starting values modifications
    starting_values = models.JSONField(default=dict)
    # Example: {"astral_energy": 20, "karma_energy": 15, "social_status": 2}
    
    # Advancement options (JSON)
    advancement_options = models.JSONField(default=dict)
    # Example: {"special_abilities": ["Kampfreflexe", "Wuchtschlag"], "talents": ["Schwerter", "Raufen"]}
    
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'characters_dsa_profession'
        verbose_name = 'DSA Profession'
        verbose_name_plural = 'DSA Professions'
    
    def __str__(self):
        return self.name
    
    def get_attribute_requirement(self, attribute):
        """Get requirement for specific attribute"""
        return self.attribute_requirements.get(attribute, 0)
    
    def get_talent_bonus(self, talent):
        """Get bonus for specific talent"""
        return self.talent_bonuses.get(talent, 0)
    
    def has_special_ability(self, ability_name):
        """Check if profession grants specific special ability"""
        return ability_name in self.granted_special_abilities
    
    def get_starting_equipment(self, equipment_type):
        """Get starting equipment of specific type"""
        return self.starting_equipment.get(equipment_type, [])
    
    def get_restriction(self, restriction_type):
        """Get profession-specific restriction"""
        return self.restrictions.get(restriction_type)
    
    def get_starting_value(self, value_type):
        """Get starting value modification"""
        return self.starting_values.get(value_type, 0)
    
    def get_advancement_option(self, option_type):
        """Get advancement options"""
        return self.advancement_options.get(option_type, [])
    
    def check_attribute_requirements(self, attributes):
        """Check if attributes meet profession requirements"""
        for attr, required_value in self.attribute_requirements.items():
            if attributes.get(attr, 0) < required_value:
                return False, f"Attribute {attr} ({attributes.get(attr, 0)}) below requirement ({required_value})"
        return True, "All requirements met"
    
    def is_magic_user(self):
        """Check if profession is magic user"""
        return self.category == 'magic'
    
    def is_clerical(self):
        """Check if profession is clerical"""
        return self.category == 'clerical'
    
    def is_combat_focused(self):
        """Check if profession is combat focused"""
        return self.category == 'combat' 