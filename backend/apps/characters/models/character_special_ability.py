import uuid
from django.db import models
from django.core.validators import MinValueValidator
from .character import Character


class CharacterSpecialAbility(models.Model):
    """
    Linking model for character special abilities
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='character_special_abilities')
    
    # Special ability type and ID (JSON)
    special_ability_data = models.JSONField()
    # Example: {"type": "general", "id": "uuid", "name": "Kampfreflexe"}
    
    # Level of the special ability (for scalable abilities)
    level = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Specializations (JSON)
    specializations = models.JSONField(default=list)
    # Example: ["Schwerter", "Säbel"] for weapon-specific abilities
    
    # Acquisition data (JSON)
    acquisition_data = models.JSONField(default=dict)
    # Example: {"acquisition_method": "purchase", "ap_cost": 10, "acquisition_date": "2025-01-26"}
    
    # Custom modifications (JSON)
    custom_modifications = models.JSONField(default=dict)
    # Example: {"custom_effects": {"attack_bonus": 1}, "custom_restrictions": ["only_against_orcs"]}
    
    # Notes and description
    notes = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chr_character_special_ability'
        verbose_name = 'Character Special Ability'
        verbose_name_plural = 'Character Special Abilities'
        unique_together = ['character', 'special_ability_data']
    
    def __str__(self):
        ability_name = self.special_ability_data.get('name', 'Unknown')
        return f"{self.character.name} - {ability_name} (Level {self.level})"
    
    def get_ability_type(self):
        """Get the type of special ability"""
        return self.special_ability_data.get('type')
    
    def get_ability_id(self):
        """Get the ID of the special ability"""
        return self.special_ability_data.get('id')
    
    def get_ability_name(self):
        """Get the name of the special ability"""
        return self.special_ability_data.get('name')
    
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
        """Get how the ability was acquired"""
        return self.acquisition_data.get('acquisition_method')
    
    def get_ap_cost(self):
        """Get AP cost for this ability"""
        return self.acquisition_data.get('ap_cost', 0)
    
    def get_acquisition_date(self):
        """Get when the ability was acquired"""
        return self.acquisition_data.get('acquisition_date')
    
    def get_custom_modification(self, modification_type):
        """Get custom modification"""
        return self.custom_modifications.get(modification_type)
    
    def add_specialization(self, specialization_type, value):
        """Add a specialization to this ability"""
        self.specializations.append({
            'type': specialization_type,
            'value': value,
            'added_at': models.DateTimeField(auto_now_add=True)
        })
        self.save()
    
    def remove_specialization(self, specialization_type):
        """Remove a specialization from this ability"""
        self.specializations = [
            spec for spec in self.specializations 
            if spec.get('type') != specialization_type
        ]
        self.save()
    
    def increase_level(self):
        """Increase the level of this ability"""
        self.level += 1
        self.save()
    
    def decrease_level(self):
        """Decrease the level of this ability"""
        if self.level > 1:
            self.level -= 1
            self.save()
    
    def get_total_ap_cost(self):
        """Get total AP cost including level increases"""
        base_cost = self.get_ap_cost()
        # Add cost for level increases (if any)
        if self.level > 1:
            # This would need to be calculated based on the specific ability's scaling
            pass
        return base_cost 