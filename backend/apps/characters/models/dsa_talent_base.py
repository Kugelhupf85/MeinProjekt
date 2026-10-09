import uuid
from django.db import models


class DSATalentBase(models.Model):
    """
    Abstract base class for all DSA talent categories
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=60, unique=True)
    # Examples: "Schwerter", "Klettern", "Überreden", "Götter/Kulte"
    
    # Governing attributes (JSON - usually 3 attributes)
    governing_attributes = models.JSONField(default=list)
    # Example: ["MU", "KL", "IN"] for most knowledge talents
    
    # Base difficulty for improvement
    improvement_factor = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')],
        default='B'
    )
    
    # Whether this talent can be used untrained
    untrained_use = models.BooleanField(default=True)
    untrained_penalty = models.IntegerField(default=0)  # Usually -3
    
    # Talent category for grouping
    talent_category = models.CharField(max_length=30, blank=True)
    # Example: "Kampf", "Körperlich", "Sozial", "Natur", "Wissen", "Sprache", "Schrift", "Handwerk", "Sonder"
    
    # Requirements (JSON)
    requirements = models.JSONField(default=dict)
    # Example: {"attributes": {"MU": 8}, "advantages": ["Magiedilettant"]}
    
    # Restrictions (JSON)
    restrictions = models.JSONField(default=dict)
    # Example: {"race_restrictions": ["Elf"], "profession_restrictions": ["Magier"]}
    
    # Special rules (JSON)
    special_rules = models.JSONField(default=dict)
    # Example: {"can_be_specialized": true, "specialization_cost": 1}
    
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return self.name
    
    def get_governing_attributes(self):
        """Get list of governing attributes"""
        return self.governing_attributes
    
    def get_improvement_factor(self):
        """Get improvement factor"""
        return self.improvement_factor
    
    def can_be_used_untrained(self):
        """Check if talent can be used untrained"""
        return self.untrained_use
    
    def get_untrained_penalty(self):
        """Get penalty for untrained use"""
        return self.untrained_penalty
    
    def get_requirement(self, requirement_type):
        """Get requirement for specific type"""
        return self.requirements.get(requirement_type)
    
    def get_restriction(self, restriction_type):
        """Get restriction for specific type"""
        return self.restrictions.get(restriction_type)
    
    def get_special_rule(self, rule_type):
        """Get special rule for specific type"""
        return self.special_rules.get(rule_type)
    
    def check_requirements(self, character_data):
        """Check if character meets talent requirements"""
        # Check attribute requirements
        attr_requirements = self.requirements.get('attributes', {})
        for attr, required_value in attr_requirements.items():
            if character_data.get('attributes', {}).get(attr, 0) < required_value:
                return False, f"Attribute {attr} below requirement ({required_value})"
        
        # Check advantage requirements
        advantage_requirements = self.requirements.get('advantages', [])
        character_advantages = [ca.advantage.name for ca in character_data.get('character_advantages', [])]
        for advantage in advantage_requirements:
            if advantage not in character_advantages:
                return False, f"Missing advantage: {advantage}"
        
        return True, "All requirements met"
    
    def check_restrictions(self, character_data):
        """Check if character meets talent restrictions"""
        # Check race restrictions
        race_restrictions = self.restrictions.get('race_restrictions', [])
        character_race = character_data.get('race')
        if race_restrictions and character_race not in race_restrictions:
            return False, f"Race '{character_race}' not allowed for this talent"
        
        # Check profession restrictions
        profession_restrictions = self.restrictions.get('profession_restrictions', [])
        character_profession = character_data.get('profession')
        if profession_restrictions and character_profession not in profession_restrictions:
            return False, f"Profession '{character_profession}' not allowed for this talent"
        
        return True, "No restrictions violated"
    
    def can_be_specialized(self):
        """Check if talent can be specialized"""
        return self.special_rules.get('can_be_specialized', False)
    
    def get_specialization_cost(self):
        """Get cost for specialization"""
        return self.special_rules.get('specialization_cost', 1) 