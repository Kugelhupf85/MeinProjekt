import uuid
from django.db import models
from django.core.validators import MinValueValidator


class DSASpecialAbilityClerical(models.Model):
    """
    DSA 4.1 Clerical Special Abilities System - Geweihte Sonderfähigkeiten
    """
    CLERICAL_TYPE_CHOICES = [
        ('liturgy', 'Liturgie'),
        ('blessing', 'Segen'),
        ('divine_magic', 'Göttliche Magie'),
        ('church_service', 'Kirchendienst'),
        ('divine_connection', 'Göttliche Verbindung'),
        ('ritual', 'Ritual')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    # Examples: "Liturgiekenntnis (Heilung)", "Göttlicher Segen", "Kirchenritual"
    
    clerical_type = models.CharField(
        max_length=20,
        choices=CLERICAL_TYPE_CHOICES,
        default='liturgy'
    )
    
    # AP (Adventure Point) Cost
    ap_cost_base = models.IntegerField(validators=[MinValueValidator(0)])
    ap_cost_per_level = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    max_levels = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Deity/Church restrictions (JSON)
    deities = models.JSONField(default=list)
    # Example: ["Praios", "Rondra", "Efferd", "Peraine"]
    
    # Liturgy categories affected (JSON)
    liturgy_categories = models.JSONField(default=list)
    # Example: ["Heilung", "Schutz", "Kampf", "Segnung"]
    
    # Specific liturgies affected (JSON)
    affected_liturgies = models.JSONField(default=list)
    # Example: ["Balsam Salabunde", "Segnung des Rondra", "Schutz des Praios"]
    
    # Requirements (JSON)
    requirements = models.JSONField(default=dict)
    # Example: {"attributes": {"MU": 13, "CH": 12}, "talents": {"Götter/Kulte": 8}, "special_abilities": ["Geweiht"]}
    
    # Effects (JSON)
    effects = models.JSONField(default=dict)
    # Example: {"liturgy_cost_reduction": 1, "liturgy_duration_bonus": 2, "karma_cost_reduction": 1}
    
    # Scaling effects (JSON)
    scaling_effects = models.JSONField(default=dict)
    # Example: {"liturgy_cost_reduction_per_level": 1, "liturgy_duration_bonus_per_level": 1}
    
    # Incompatible with (JSON list)
    incompatible_with = models.JSONField(default=list)
    # Example: ["Liturgiekenntnis (Dämonisch)", "Göttlicher Fluch"]
    
    # Clerical-specific restrictions
    restrictions = models.JSONField(default=dict)
    # Example: {"max_levels_per_character": 1, "deity_restrictions": ["nur_praios"]}
    
    # Prerequisites (JSON)
    prerequisites = models.JSONField(default=dict)
    # Example: {"advantages": ["Geweiht"], "professions": ["Geweihter"]}
    
    # Clerical mechanics (JSON)
    clerical_mechanics = models.JSONField(default=dict)
    # Example: {"casting_time_modifier": -1, "karma_cost_reduction": 2, "liturgy_difficulty_modifier": -1}
    
    # Divine connection data (JSON)
    divine_connection_data = models.JSONField(default=dict)
    # Example: {"connection_strength": 3, "divine_favor": 2, "miracles_possible": true}
    
    # Church service requirements (JSON)
    church_service_requirements = models.JSONField(default=dict)
    # Example: {"weekly_service": true, "temple_duties": ["Opfer", "Segnung"], "prayer_requirements": 3}
    
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chr_dsa_special_ability_clerical'
        verbose_name = 'DSA Clerical Special Ability'
        verbose_name_plural = 'DSA Clerical Special Abilities'
    
    def __str__(self):
        return f"{self.name} ({self.get_clerical_type_display()})"
    
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
    
    def is_applicable_to_deity(self, deity_name):
        """Check if ability is applicable to specific deity"""
        return not self.deities or deity_name in self.deities
    
    def is_applicable_to_category(self, category_name):
        """Check if ability is applicable to specific liturgy category"""
        return not self.liturgy_categories or category_name in self.liturgy_categories
    
    def is_applicable_to_liturgy(self, liturgy_name):
        """Check if ability is applicable to specific liturgy"""
        return not self.affected_liturgies or liturgy_name in self.affected_liturgies
    
    def get_clerical_mechanic(self, mechanic_type):
        """Get specific clerical mechanic"""
        return self.clerical_mechanics.get(mechanic_type)
    
    def get_divine_connection_data(self, data_type):
        """Get specific divine connection data"""
        return self.divine_connection_data.get(data_type)
    
    def get_church_service_requirement(self, requirement_type):
        """Get specific church service requirement"""
        return self.church_service_requirements.get(requirement_type)
    
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