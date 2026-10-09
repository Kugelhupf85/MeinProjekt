from django.db import models
from .dsa_talent_base import DSATalentBase


class DSATalentSocial(DSATalentBase):
    """
    DSA 4.1 Social Talents - Soziale Talente
    """
    SOCIAL_TYPE_CHOICES = [
        ('communication', 'Kommunikation'),
        ('influence', 'Einflussnahme'),
        ('leadership', 'Führung'),
        ('deception', 'Täuschung'),
        ('empathy', 'Empathie')
    ]
    
    social_type = models.CharField(
        max_length=20,
        choices=SOCIAL_TYPE_CHOICES,
        default='communication'
    )
    
    # Social context restrictions (JSON)
    social_contexts = models.JSONField(default=list)
    # Example: ["noble_court", "merchant_guild", "common_folk", "criminal_underworld"]
    
    # Social-specific bonuses (JSON)
    social_bonuses = models.JSONField(default=dict)
    # Example: {"reputation_bonus": 1, "trust_bonus": 1, "influence_bonus": 1}
    
    # Special social rules (JSON)
    social_rules = models.JSONField(default=dict)
    # Example: {"can_read_emotions": true, "special_persuasion_options": ["Intimidation"]}
    
    # Requirements for social use (JSON)
    social_requirements = models.JSONField(default=dict)
    # Example: {"status_requirements": ["noble"], "appearance_requirements": ["presentable"]}
    
    class Meta:
        db_table = 'chr_dsa_talent_social'
        verbose_name = 'DSA Social Talent'
        verbose_name_plural = 'DSA Social Talents'
    
    def __str__(self):
        return f"{self.name} ({self.get_social_type_display()})"
    
    def is_applicable_in_context(self, context_name):
        """Check if talent is applicable in specific social context"""
        return not self.social_contexts or context_name in self.social_contexts
    
    def get_social_bonus(self, bonus_type):
        """Get specific social bonus"""
        return self.social_bonuses.get(bonus_type, 0)
    
    def get_social_rule(self, rule_type):
        """Get specific social rule"""
        return self.social_rules.get(rule_type)
    
    def get_social_requirement(self, requirement_type):
        """Get specific social requirement"""
        return self.social_requirements.get(requirement_type)
    
    def check_social_requirements(self, character_data, social_context=None):
        """Check if character meets social-specific requirements"""
        # Check status requirements
        status_requirements = self.social_requirements.get('status_requirements', [])
        character_status = character_data.get('social_status')
        if status_requirements and character_status not in status_requirements:
            return False, f"Social status '{character_status}' not sufficient"
        
        # Check appearance requirements
        appearance_requirements = self.social_requirements.get('appearance_requirements', [])
        character_appearance = character_data.get('appearance_quality')
        if appearance_requirements and character_appearance not in appearance_requirements:
            return False, f"Appearance quality '{character_appearance}' not sufficient"
        
        return True, "All social requirements met" 