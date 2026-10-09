import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class CharacterAdvantage(models.Model):
    """
    Linking model for Character-Advantage relationships
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    character = models.ForeignKey('Character', on_delete=models.CASCADE, related_name='character_advantages')
    advantage = models.ForeignKey('DSAAdvantage', on_delete=models.PROTECT, related_name='character_advantages')
    
    # Level of the advantage (for scalable advantages)
    level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Custom modifications for this character (JSON)
    custom_modifiers = models.JSONField(default=dict, blank=True)
    # Example: {"life_points_bonus": 2, "custom_effect": "Special bonus"}
    
    # Acquisition data
    acquired_at = models.DateTimeField(auto_now_add=True)
    acquisition_notes = models.TextField(blank=True)
    
    # Validation status
    is_valid = models.BooleanField(default=True)
    validation_errors = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'characters_character_advantage'
        unique_together = ['character', 'advantage']
        verbose_name = 'Character Advantage'
        verbose_name_plural = 'Character Advantages'
    
    def __str__(self):
        return f"{self.character.name} - {self.advantage.name} (Level {self.level})"
    
    def clean(self):
        """Validate character advantage"""
        super().clean()
        
        # Check level limits
        if self.level > self.advantage.max_levels:
            from django.core.exceptions import ValidationError
            raise ValidationError(f"Level {self.level} exceeds maximum {self.advantage.max_levels}")
        
        # Check for incompatible advantages
        for incompatible in self.advantage.incompatible_with:
            if self.character.character_advantages.filter(advantage__name=incompatible).exists():
                from django.core.exceptions import ValidationError
                raise ValidationError(f"Incompatible with {incompatible}")
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def gp_cost(self):
        """Get GP cost for this advantage level"""
        return self.advantage.get_gp_cost(self.level)
    
    @property
    def total_effects(self):
        """Get total effects including custom modifiers"""
        base_effects = {}
        
        # Get base effects from advantage
        for effect_type, base_value in self.advantage.effects.items():
            base_effects[effect_type] = base_value
        
        # Apply scaling effects
        for effect_type, scaling_value in self.advantage.scaling_effects.items():
            base_effect_type = effect_type.replace('_per_level', '')
            if base_effect_type in base_effects:
                base_effects[base_effect_type] += scaling_value * (self.level - 1)
        
        # Apply custom modifiers
        for modifier_type, modifier_value in self.custom_modifiers.items():
            if modifier_type in base_effects:
                base_effects[modifier_type] += modifier_value
            else:
                base_effects[modifier_type] = modifier_value
        
        return base_effects
    
    def get_effect(self, effect_type):
        """Get specific effect value"""
        return self.total_effects.get(effect_type, 0)
    
    def add_custom_modifier(self, modifier_type, value):
        """Add custom modifier"""
        self.custom_modifiers[modifier_type] = value
        self.save()
    
    def remove_custom_modifier(self, modifier_type):
        """Remove custom modifier"""
        if modifier_type in self.custom_modifiers:
            del self.custom_modifiers[modifier_type]
            self.save()
    
    def validate_requirements(self):
        """Validate if character still meets advantage requirements"""
        character_data = {
            'attributes': self.character.core_attributes,
            'advantages': [ca.advantage.name for ca in self.character.character_advantages.exclude(id=self.id)]
        }
        
        is_valid, message = self.advantage.check_requirements(character_data)
        self.is_valid = is_valid
        
        if not is_valid:
            if message not in self.validation_errors:
                self.validation_errors.append(message)
        else:
            self.validation_errors = []
        
        self.save()
        return is_valid, message 