import uuid
from django.db import models


class DSACulture(models.Model):
    """
    DSA 4.1 Culture System - Kulturen mit Language- und Skill-Boni
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50, unique=True)
    # Examples: "Mittelreich", "Horasreich", "Bornland", "Thorwal"
    
    # Language Bonuses (JSON)
    language_bonuses = models.JSONField(default=dict)
    # Example: {"Garethi": 10, "Bosparano": 7, "Alaani": 4}
    
    # Script Bonuses (JSON) 
    script_bonuses = models.JSONField(default=dict)
    # Example: {"Kusliker Zeichen": 8, "Imperiale Zeichen": 5}
    
    # Talent Modifications (JSON)
    talent_modifications = models.JSONField(default=dict)
    # Example: {"Reiten": 2, "Schwimmen": -2, "Singen": 1}
    
    # Typical Professions (JSON list)
    typical_professions = models.JSONField(default=list)
    # Example: ["Krieger", "Handwerker", "Gelehrter"]
    
    # Social Status Range
    social_status_min = models.IntegerField(default=1)
    social_status_max = models.IntegerField(default=6)
    
    # Culture-specific restrictions
    restrictions = models.JSONField(default=dict)
    # Example: {"forbidden_professions": ["Geweihter"], "required_advantages": ["Soziale Anpassung"]}
    
    # Starting equipment modifications
    starting_equipment_modifications = models.JSONField(default=dict)
    # Example: {"additional_money": 50, "additional_weapons": ["Dolch"]}
    
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'characters_dsa_culture'
        verbose_name = 'DSA Culture'
        verbose_name_plural = 'DSA Cultures'
    
    def __str__(self):
        return self.name
    
    def get_language_bonus(self, language):
        """Get bonus for specific language"""
        return self.language_bonuses.get(language, 0)
    
    def get_script_bonus(self, script):
        """Get bonus for specific script"""
        return self.script_bonuses.get(script, 0)
    
    def get_talent_modification(self, talent):
        """Get modification for specific talent"""
        return self.talent_modifications.get(talent, 0)
    
    def is_typical_profession(self, profession):
        """Check if profession is typical for this culture"""
        return profession in self.typical_professions
    
    def get_restriction(self, restriction_type):
        """Get culture-specific restriction"""
        return self.restrictions.get(restriction_type)
    
    def get_equipment_modification(self, modification_type):
        """Get starting equipment modification"""
        return self.starting_equipment_modifications.get(modification_type)
    
    def is_social_status_valid(self, status):
        """Check if social status is valid for this culture"""
        return self.social_status_min <= status <= self.social_status_max 