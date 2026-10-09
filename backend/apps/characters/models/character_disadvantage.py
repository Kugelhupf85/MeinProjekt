import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class CharacterDisadvantage(models.Model):
    """
    Linking model for Character-Disadvantage relationships
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    character = models.ForeignKey('Character', on_delete=models.CASCADE, related_name='character_disadvantages')
    disadvantage = models.ForeignKey('DSADisadvantage', on_delete=models.PROTECT, related_name='character_disadvantages')
    
    # Level of the disadvantage (for scalable disadvantages)
    level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Custom modifications for this character (JSON)
    custom_modifiers = models.JSONField(default=dict, blank=True)
    # Example: {"life_points_penalty": -2, "custom_effect": "Special penalty"}
    
    # Acquisition data
    acquired_at = models.DateTimeField(auto_now_add=True)
    acquisition_notes = models.TextField(blank=True)
    
    # Validation status
    is_valid = models.BooleanField(default=True)
    validation_errors = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'characters_character_disadvantage'
        unique_together = ['character', 'disadvantage']
        verbose_name = 'Character Disadvantage'
        verbose_name_plural = 'Character Disadvantages'
    
    def __str__(self):
        return f"{self.character.name} - {self.disadvantage.name} (Level {self.level})"
    
    def clean(self):
        """Validate character disadvantage"""
        super().clean()
        
        # Check level limits
        if self.level > self.disadvantage.max_levels:
            from django.core.exceptions import ValidationError
            raise ValidationError(f"Level {self.level} exceeds maximum {self.disadvantage.max_levels}")
        
        # Check for incompatible disadvantages
        for incompatible in self.disadvantage.incompatible_with:
            if self.character.character_disadvantages.filter(disadvantage__name=incompatible).exists():
                from django.core.exceptions import ValidationError
                raise ValidationError(f"Incompatible with {incompatible}")
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def gp_gain(self):
        """Get GP gain for this disadvantage level"""
        return self.disadvantage.get_gp_gain(self.level)
    
    @property
    def total_effects(self):
        """Get total effects including custom modifiers"""
        base_effects = {}
        
        # Get base effects from disadvantage
        for effect_type, base_value in self.disadvantage.effects.items():
            base_effects[effect_type] = base_value
        
        # Apply scaling effects
        for effect_type, scaling_value in self.disadvantage.scaling_effects.items():
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
        """Validate if character still meets disadvantage requirements"""
        character_data = {
            'attributes': self.character.core_attributes,
            'profession': getattr(self.character.ruleset_data, 'profession', None)
        }
        
        is_valid, message = self.disadvantage.check_requirements(character_data)
        self.is_valid = is_valid
        
        if not is_valid:
            if message not in self.validation_errors:
                self.validation_errors.append(message)
        else:
            self.validation_errors = []
        
        self.save()
        return is_valid, message 