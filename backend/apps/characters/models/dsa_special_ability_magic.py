import uuid
from django.db import models
from django.core.validators import MinValueValidator


class DSASpecialAbilityMagic(models.Model):
    """
    DSA 4.1 Magic Special Abilities System - Magische Sonderfähigkeiten
    """
    MAGIC_TYPE_CHOICES = [
        ('general', 'Magisch'),
        ('spell_knowledge', 'Merkmalskenntnis'),
        ('object_ritual', 'Objektritual'),
        ('ritual_knowledge', 'Ritualkenntnis'),
        ('magical_tradition', 'Magische Tradition'),
        ('spell_modification', 'Zaubermodifikation')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    # Examples: "Merkmalskenntnis (Elementar)", "Objektritual (Schwert)", "Ritualkenntnis (Heilung)"
    
    magic_type = models.CharField(
        max_length=20,
        choices=MAGIC_TYPE_CHOICES,
        default='general'
    )
    
    # AP (Adventure Point) Cost
    ap_cost_base = models.IntegerField(validators=[MinValueValidator(0)])
    ap_cost_per_level = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    max_levels = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Magic school/tradition restrictions (JSON)
    magic_traditions = models.JSONField(default=list)
    # Example: ["Gildenmagier", "Hexe", "Druide", "Geode"]
    
    # Spell/Ritual categories affected (JSON)
    affected_categories = models.JSONField(default=list)
    # Example: ["Elementar", "Heilung", "Illusion"] for Merkmalskenntnis
    
    # Specific spells/rituals affected (JSON)
    affected_spells = models.JSONField(default=list)
    # Example: ["Ignifaxius", "Balsam Salabunde"] for specific spell modifications
    
    # Requirements (JSON)
    requirements = models.JSONField(default=dict)
    # Example: {"attributes": {"MU": 13, "KL": 11}, "talents": {"Magiekunde": 8}, "special_abilities": ["Magiedilettant"]}
    
    # Effects (JSON)
    effects = models.JSONField(default=dict)
    # Example: {"spell_cost_reduction": 1, "spell_duration_bonus": 2, "spell_range_bonus": 1}
    
    # Scaling effects (JSON)
    scaling_effects = models.JSONField(default=dict)
    # Example: {"spell_cost_reduction_per_level": 1, "spell_duration_bonus_per_level": 1}
    
    # Incompatible with (JSON list)
    incompatible_with = models.JSONField(default=list)
    # Example: ["Merkmalskenntnis (Dämonisch)", "Objektritual (Schild)"]
    
    # Magic-specific restrictions
    restrictions = models.JSONField(default=dict)
    # Example: {"max_levels_per_character": 1, "tradition_restrictions": ["nur_gildenmagier"]}
    
    # Prerequisites (JSON)
    prerequisites = models.JSONField(default=dict)
    # Example: {"advantages": ["Magiedilettant"], "professions": ["Magier"]}
    
    # Magic mechanics (JSON)
    magic_mechanics = models.JSONField(default=dict)
    # Example: {"casting_time_modifier": -1, "astral_cost_reduction": 2, "spell_difficulty_modifier": -1}
    
    # Object ritual specific data (JSON)
    object_ritual_data = models.JSONField(default=dict)
    # Example: {"object_type": "weapon", "enchantment_type": "combat", "duration": "permanent"}
    
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chr_dsa_special_ability_magic'
        verbose_name = 'DSA Magic Special Ability'
        verbose_name_plural = 'DSA Magic Special Abilities'
    
    def __str__(self):
        return f"{self.name} ({self.get_magic_type_display()})"
    
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
    
    def is_applicable_to_tradition(self, tradition_name):
        """Check if ability is applicable to specific magic tradition"""
        return not self.magic_traditions or tradition_name in self.magic_traditions
    
    def is_applicable_to_category(self, category_name):
        """Check if ability is applicable to specific spell category"""
        return not self.affected_categories or category_name in self.affected_categories
    
    def is_applicable_to_spell(self, spell_name):
        """Check if ability is applicable to specific spell"""
        return not self.affected_spells or spell_name in self.affected_spells
    
    def get_magic_mechanic(self, mechanic_type):
        """Get specific magic mechanic"""
        return self.magic_mechanics.get(mechanic_type)
    
    def get_object_ritual_data(self, data_type):
        """Get specific object ritual data"""
        return self.object_ritual_data.get(data_type)
    
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
        
        # Check profession requirements
        profession_requirements = self.prerequisites.get('professions', [])
        character_profession = character_data.get('profession')
        if profession_requirements and character_profession not in profession_requirements:
            return False, f"Profession '{character_profession}' not in required professions"
        
        return True, "All requirements met"
    
    def is_scalable(self):
        """Check if ability is scalable (multiple levels)"""
        return self.max_levels > 1
    
    def get_total_ap_cost(self):
        """Get total AP cost for maximum levels"""
        if self.is_scalable():
            return sum(self.get_ap_cost(level) for level in range(1, self.max_levels + 1))
        return self.ap_cost_base 