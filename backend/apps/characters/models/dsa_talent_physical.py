from django.db import models
from .dsa_talent_base import DSATalentBase


class DSATalentPhysical(DSATalentBase):
    """
    DSA 4.1 Physical Talents - Körperliche Talente
    """
    PHYSICAL_TYPE_CHOICES = [
        ('movement', 'Bewegung'),
        ('athletics', 'Athletik'),
        ('survival', 'Überleben'),
        ('stealth', 'Heimlichkeit'),
        ('perception', 'Wahrnehmung')
    ]
    
    physical_type = models.CharField(
        max_length=20,
        choices=PHYSICAL_TYPE_CHOICES,
        default='movement'
    )
    
    # Physical context restrictions (JSON)
    physical_contexts = models.JSONField(default=list)
    # Example: ["urban", "wilderness", "underground", "water", "air"]
    
    # Physical-specific bonuses (JSON)
    physical_bonuses = models.JSONField(default=dict)
    # Example: {"movement_bonus": 1, "endurance_bonus": 1, "stealth_bonus": 1}
    
    # Special physical rules (JSON)
    physical_rules = models.JSONField(default=dict)
    # Example: {"can_move_silently": true, "special_movement_options": ["Climbing"]}
    
    # Requirements for physical use (JSON)
    physical_requirements = models.JSONField(default=dict)
    # Example: {"equipment_requirements": ["climbing_gear"], "condition_requirements": ["not_encumbered"]}
    
    # Environmental modifiers (JSON)
    environmental_modifiers = models.JSONField(default=dict)
    # Example: {"wet_ground": -2, "darkness": -1, "difficult_terrain": -3}
    
    class Meta:
        db_table = 'chr_dsa_talent_physical'
        verbose_name = 'DSA Physical Talent'
        verbose_name_plural = 'DSA Physical Talents'
    
    def __str__(self):
        return f"{self.name} ({self.get_physical_type_display()})"
    
    def is_applicable_in_context(self, context_name):
        """Check if talent is applicable in specific physical context"""
        return not self.physical_contexts or context_name in self.physical_contexts
    
    def get_physical_bonus(self, bonus_type):
        """Get specific physical bonus"""
        return self.physical_bonuses.get(bonus_type, 0)
    
    def get_physical_rule(self, rule_type):
        """Get specific physical rule"""
        return self.physical_rules.get(rule_type)
    
    def get_physical_requirement(self, requirement_type):
        """Get specific physical requirement"""
        return self.physical_requirements.get(requirement_type)
    
    def get_environmental_modifier(self, condition):
        """Get environmental modifier for specific condition"""
        return self.environmental_modifiers.get(condition, 0)
    
    def check_physical_requirements(self, character_data, equipment_data=None, condition_data=None):
        """Check if character meets physical-specific requirements"""
        # Check equipment requirements
        equipment_requirements = self.physical_requirements.get('equipment_requirements', [])
        if equipment_requirements and equipment_data:
            for required_equipment in equipment_requirements:
                if required_equipment not in equipment_data:
                    return False, f"Required equipment '{required_equipment}' not available"
        
        # Check condition requirements
        condition_requirements = self.physical_requirements.get('condition_requirements', [])
        if condition_requirements and condition_data:
            for required_condition in condition_requirements:
                if not condition_data.get(required_condition, False):
                    return False, f"Required condition '{required_condition}' not met"
        
        return True, "All physical requirements met" 