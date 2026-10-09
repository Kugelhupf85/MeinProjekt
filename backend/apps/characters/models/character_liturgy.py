import uuid
from django.db import models
from django.core.validators import MinValueValidator
from .character import Character


class CharacterLiturgy(models.Model):
    """
    Character liturgies and divine abilities
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='character_liturgies')
    
    # Liturgy data (JSON)
    liturgy_data = models.JSONField()
    # Example: {"name": "Balsam Salabunde", "category": "Heilung", "difficulty": 6, "karma_cost": 2}
    
    # Current level/mastery of the liturgy
    level = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Liturgy modifications (JSON)
    modifications = models.JSONField(default=dict)
    # Example: {"extended_duration": true, "reduced_karma_cost": 1, "custom_effects": ["healing_bonus"]}
    
    # Acquisition data (JSON)
    acquisition_data = models.JSONField(default=dict)
    # Example: {"acquisition_method": "divine_gift", "ap_cost": 12, "acquisition_date": "2025-01-26"}
    
    # Deity association (JSON)
    deity_data = models.JSONField(default=dict)
    # Example: {"deity": "Peraine", "favor_level": 3, "temple_connection": "Gareth"}
    
    # Casting history (JSON)
    casting_history = models.JSONField(default=list)
    # Example: [{"date": "2025-01-26", "success": true, "deity_favor": 2, "modifiers": ["extended_duration"]}]
    
    # Notes and description
    notes = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chr_character_liturgy'
        verbose_name = 'Character Liturgy'
        verbose_name_plural = 'Character Liturgies'
        unique_together = ['character', 'liturgy_data']
    
    def __str__(self):
        liturgy_name = self.liturgy_data.get('name', 'Unknown')
        return f"{self.character.name} - {liturgy_name} (Level {self.level})"
    
    def get_liturgy_name(self):
        """Get the name of the liturgy"""
        return self.liturgy_data.get('name')
    
    def get_liturgy_category(self):
        """Get the category of the liturgy"""
        return self.liturgy_data.get('category')
    
    def get_liturgy_difficulty(self):
        """Get the base difficulty of the liturgy"""
        return self.liturgy_data.get('difficulty', 0)
    
    def get_liturgy_karma_cost(self):
        """Get the base karma cost of the liturgy"""
        return self.liturgy_data.get('karma_cost', 0)
    
    def get_effective_difficulty(self):
        """Get effective difficulty including modifications"""
        base_difficulty = self.get_liturgy_difficulty()
        difficulty_modifier = self.modifications.get('difficulty_modifier', 0)
        return max(1, base_difficulty + difficulty_modifier)
    
    def get_effective_karma_cost(self):
        """Get effective karma cost including modifications"""
        base_cost = self.get_liturgy_karma_cost()
        cost_reduction = self.modifications.get('karma_cost_reduction', 0)
        return max(1, base_cost - cost_reduction)
    
    def get_modification(self, modification_type):
        """Get specific modification"""
        return self.modifications.get(modification_type)
    
    def has_modification(self, modification_type):
        """Check if liturgy has specific modification"""
        return modification_type in self.modifications
    
    def add_modification(self, modification_type, value):
        """Add a modification to this liturgy"""
        self.modifications[modification_type] = value
        self.save()
    
    def remove_modification(self, modification_type):
        """Remove a modification from this liturgy"""
        if modification_type in self.modifications:
            del self.modifications[modification_type]
            self.save()
    
    def get_acquisition_method(self):
        """Get how the liturgy was acquired"""
        return self.acquisition_data.get('acquisition_method')
    
    def get_ap_cost(self):
        """Get AP cost for this liturgy"""
        return self.acquisition_data.get('ap_cost', 0)
    
    def get_acquisition_date(self):
        """Get when the liturgy was acquired"""
        return self.acquisition_data.get('acquisition_date')
    
    def get_deity(self):
        """Get associated deity"""
        return self.deity_data.get('deity')
    
    def get_favor_level(self):
        """Get deity favor level"""
        return self.deity_data.get('favor_level', 0)
    
    def get_temple_connection(self):
        """Get temple connection"""
        return self.deity_data.get('temple_connection')
    
    def increase_level(self):
        """Increase the level of this liturgy"""
        self.level += 1
        self.save()
    
    def decrease_level(self):
        """Decrease the level of this liturgy"""
        if self.level > 1:
            self.level -= 1
            self.save()
    
    def add_casting_record(self, success, deity_favor=None, modifiers=None):
        """Add a casting record to history"""
        casting_record = {
            'date': models.DateTimeField(auto_now_add=True),
            'success': success,
            'deity_favor': deity_favor or self.get_favor_level(),
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
        """Get total AP cost for this liturgy"""
        base_cost = self.get_ap_cost()
        # Add cost for level increases (if any)
        if self.level > 1:
            # This would need to be calculated based on the liturgy's scaling
            pass
        return base_cost 