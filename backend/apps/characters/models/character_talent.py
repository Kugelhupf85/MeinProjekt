import uuid
from django.db import models
from django.core.validators import MinValueValidator
from .character import Character


class CharacterTalent(models.Model):
    """
    Linking model for character talents
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='character_talents')
    
    # Talent type and ID (JSON)
    talent_data = models.JSONField()
    # Example: {"type": "combat", "id": "uuid", "name": "Schwerter"}
    
    # Current value of the talent
    value = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Specializations (JSON)
    specializations = models.JSONField(default=list)
    # Example: [{"type": "weapon", "value": "Anderthalbhänder"}, {"type": "style", "value": "Defensive"}]
    
    # Acquisition data (JSON)
    acquisition_data = models.JSONField(default=dict)
    # Example: {"acquisition_method": "culture_bonus", "ap_cost": 0, "acquisition_date": "2025-01-26"}
    
    # Custom modifications (JSON)
    custom_modifications = models.JSONField(default=dict)
    # Example: {"custom_bonuses": {"attack_bonus": 1}, "custom_restrictions": ["only_against_orcs"]}
    
    # Notes and description
    notes = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chr_character_talent'
        verbose_name = 'Character Talent'
        verbose_name_plural = 'Character Talents'
        unique_together = ['character', 'talent_data']
    
    def __str__(self):
        talent_name = self.talent_data.get('name', 'Unknown')
        return f"{self.character.name} - {talent_name} ({self.value})"
    
    def get_talent_type(self):
        """Get the type of talent"""
        return self.talent_data.get('type')
    
    def get_talent_id(self):
        """Get the ID of the talent"""
        return self.talent_data.get('id')
    
    def get_talent_name(self):
        """Get the name of the talent"""
        return self.talent_data.get('name')
    
    def get_specialization(self, specialization_type):
        """Get specific specialization"""
        for spec in self.specializations:
            if spec.get('type') == specialization_type:
                return spec.get('value')
        return None
    
    def has_specialization(self, specialization_type):
        """Check if character has specific specialization"""
        return any(spec.get('type') == specialization_type for spec in self.specializations)
    
    def get_acquisition_method(self):
        """Get how the talent was acquired"""
        return self.acquisition_data.get('acquisition_method')
    
    def get_ap_cost(self):
        """Get AP cost for this talent"""
        return self.acquisition_data.get('ap_cost', 0)
    
    def get_acquisition_date(self):
        """Get when the talent was acquired"""
        return self.acquisition_data.get('acquisition_date')
    
    def get_custom_modification(self, modification_type):
        """Get custom modification"""
        return self.custom_modifications.get(modification_type)
    
    def add_specialization(self, specialization_type, value):
        """Add a specialization to this talent"""
        self.specializations.append({
            'type': specialization_type,
            'value': value,
            'added_at': models.DateTimeField(auto_now_add=True)
        })
        self.save()
    
    def remove_specialization(self, specialization_type):
        """Remove a specialization from this talent"""
        self.specializations = [
            spec for spec in self.specializations 
            if spec.get('type') != specialization_type
        ]
        self.save()
    
    def increase_value(self, amount=1):
        """Increase the value of this talent"""
        self.value += amount
        self.save()
    
    def decrease_value(self, amount=1):
        """Decrease the value of this talent"""
        if self.value >= amount:
            self.value -= amount
            self.save()
    
    def set_value(self, new_value):
        """Set the value of this talent"""
        if new_value >= 0:
            self.value = new_value
            self.save()
    
    def get_total_ap_cost(self):
        """Get total AP cost for this talent"""
        base_cost = self.get_ap_cost()
        # Add cost for value increases (if any)
        if self.value > 0:
            # This would need to be calculated based on the talent's improvement factor
            pass
        return base_cost
    
    def get_effective_value(self, context_data=None):
        """Get effective value including bonuses and modifiers"""
        effective_value = self.value
        
        # Add custom bonuses
        custom_bonuses = self.custom_modifications.get('custom_bonuses', {})
        for bonus_type, bonus_value in custom_bonuses.items():
            effective_value += bonus_value
        
        # Add context-specific bonuses (if context data provided)
        if context_data:
            context_bonuses = self.custom_modifications.get('context_bonuses', {})
            for context_type, bonus_value in context_bonuses.items():
                if context_data.get(context_type):
                    effective_value += bonus_value
        
        return max(0, effective_value) 