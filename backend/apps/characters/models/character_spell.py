import uuid
from django.db import models
from django.core.validators import MinValueValidator
from .character import Character


class CharacterSpell(models.Model):
    """
    Character spells and magical abilities
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='character_spells')
    
    # Spell data (JSON)
    spell_data = models.JSONField()
    # Example: {"name": "Ignifaxius", "category": "Elementar", "difficulty": 8, "cost": 4}
    
    # Current level/mastery of the spell
    level = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Spell modifications (JSON)
    modifications = models.JSONField(default=dict)
    # Example: {"extended_range": true, "reduced_cost": 1, "custom_effects": ["fire_damage_bonus"]}
    
    # Acquisition data (JSON)
    acquisition_data = models.JSONField(default=dict)
    # Example: {"acquisition_method": "study", "ap_cost": 15, "acquisition_date": "2025-01-26"}
    
    # Casting history (JSON)
    casting_history = models.JSONField(default=list)
    # Example: [{"date": "2025-01-26", "success": true, "modifiers": ["extended_range"]}]
    
    # Notes and description
    notes = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chr_character_spell'
        verbose_name = 'Character Spell'
        verbose_name_plural = 'Character Spells'
        unique_together = ['character', 'spell_data']
    
    def __str__(self):
        spell_name = self.spell_data.get('name', 'Unknown')
        return f"{self.character.name} - {spell_name} (Level {self.level})"
    
    def get_spell_name(self):
        """Get the name of the spell"""
        return self.spell_data.get('name')
    
    def get_spell_category(self):
        """Get the category of the spell"""
        return self.spell_data.get('category')
    
    def get_spell_difficulty(self):
        """Get the base difficulty of the spell"""
        return self.spell_data.get('difficulty', 0)
    
    def get_spell_cost(self):
        """Get the base cost of the spell"""
        return self.spell_data.get('cost', 0)
    
    def get_effective_difficulty(self):
        """Get effective difficulty including modifications"""
        base_difficulty = self.get_spell_difficulty()
        difficulty_modifier = self.modifications.get('difficulty_modifier', 0)
        return max(1, base_difficulty + difficulty_modifier)
    
    def get_effective_cost(self):
        """Get effective cost including modifications"""
        base_cost = self.get_spell_cost()
        cost_reduction = self.modifications.get('cost_reduction', 0)
        return max(1, base_cost - cost_reduction)
    
    def get_modification(self, modification_type):
        """Get specific modification"""
        return self.modifications.get(modification_type)
    
    def has_modification(self, modification_type):
        """Check if spell has specific modification"""
        return modification_type in self.modifications
    
    def add_modification(self, modification_type, value):
        """Add a modification to this spell"""
        self.modifications[modification_type] = value
        self.save()
    
    def remove_modification(self, modification_type):
        """Remove a modification from this spell"""
        if modification_type in self.modifications:
            del self.modifications[modification_type]
            self.save()
    
    def get_acquisition_method(self):
        """Get how the spell was acquired"""
        return self.acquisition_data.get('acquisition_method')
    
    def get_ap_cost(self):
        """Get AP cost for this spell"""
        return self.acquisition_data.get('ap_cost', 0)
    
    def get_acquisition_date(self):
        """Get when the spell was acquired"""
        return self.acquisition_data.get('acquisition_date')
    
    def increase_level(self):
        """Increase the level of this spell"""
        self.level += 1
        self.save()
    
    def decrease_level(self):
        """Decrease the level of this spell"""
        if self.level > 1:
            self.level -= 1
            self.save()
    
    def add_casting_record(self, success, modifiers=None):
        """Add a casting record to history"""
        casting_record = {
            'date': models.DateTimeField(auto_now_add=True),
            'success': success,
            'modifiers': modifiers or []
        }
        self.casting_history.append(casting_record)
        self.save()
    
    def get_casting_success_rate(self):
        """Get casting success rate from history"""
        if not self.casting_history:
            return 0.0
        
        successful_casts = sum(1 for record in self.casting_history if record.get('success', False))
        return successful_casts / len(self.casting_history)
    
    def get_total_ap_cost(self):
        """Get total AP cost for this spell"""
        base_cost = self.get_ap_cost()
        # Add cost for level increases (if any)
        if self.level > 1:
            # This would need to be calculated based on the spell's scaling
            pass
        return base_cost 