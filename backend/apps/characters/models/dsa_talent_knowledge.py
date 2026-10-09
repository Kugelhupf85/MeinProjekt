from django.db import models
from .dsa_talent_base import DSATalentBase


class DSATalentKnowledge(DSATalentBase):
    """
    DSA 4.1 Knowledge Talents - Wissens- und Sprachtalente
    """
    KNOWLEDGE_TYPE_CHOICES = [
        ('academic', 'Akademisch'),
        ('practical', 'Praktisch'),
        ('language', 'Sprache'),
        ('script', 'Schrift'),
        ('lore', 'Sagenkunde'),
        ('craft', 'Handwerk')
    ]
    
    knowledge_type = models.CharField(
        max_length=20,
        choices=KNOWLEDGE_TYPE_CHOICES,
        default='academic'
    )
    
    # Knowledge domain restrictions (JSON)
    knowledge_domains = models.JSONField(default=list)
    # Example: ["history", "magic", "nature", "religion", "politics"]
    
    # Knowledge-specific bonuses (JSON)
    knowledge_bonuses = models.JSONField(default=dict)
    # Example: {"research_bonus": 1, "identification_bonus": 1, "translation_bonus": 1}
    
    # Special knowledge rules (JSON)
    knowledge_rules = models.JSONField(default=dict)
    # Example: {"can_read_ancient_texts": true, "special_research_options": ["Archaeology"]}
    
    # Requirements for knowledge use (JSON)
    knowledge_requirements = models.JSONField(default=dict)
    # Example: {"education_requirements": ["university"], "access_requirements": ["library"]}
    
    # For language talents: difficulty and script
    language_difficulty = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')],
        blank=True
    )
    script_required = models.CharField(max_length=30, blank=True)
    # Example: "Garethi", "Tulamidya", "Ancient"
    
    class Meta:
        db_table = 'chr_dsa_talent_knowledge'
        verbose_name = 'DSA Knowledge Talent'
        verbose_name_plural = 'DSA Knowledge Talents'
    
    def __str__(self):
        return f"{self.name} ({self.get_knowledge_type_display()})"
    
    def is_applicable_to_domain(self, domain_name):
        """Check if talent is applicable to specific knowledge domain"""
        return not self.knowledge_domains or domain_name in self.knowledge_domains
    
    def get_knowledge_bonus(self, bonus_type):
        """Get specific knowledge bonus"""
        return self.knowledge_bonuses.get(bonus_type, 0)
    
    def get_knowledge_rule(self, rule_type):
        """Get specific knowledge rule"""
        return self.knowledge_rules.get(rule_type)
    
    def get_knowledge_requirement(self, requirement_type):
        """Get specific knowledge requirement"""
        return self.knowledge_requirements.get(requirement_type)
    
    def check_knowledge_requirements(self, character_data, research_context=None):
        """Check if character meets knowledge-specific requirements"""
        # Check education requirements
        education_requirements = self.knowledge_requirements.get('education_requirements', [])
        character_education = character_data.get('education_level')
        if education_requirements and character_education not in education_requirements:
            return False, f"Education level '{character_education}' not sufficient"
        
        # Check access requirements
        access_requirements = self.knowledge_requirements.get('access_requirements', [])
        if access_requirements and research_context:
            if research_context not in access_requirements:
                return False, f"Research context '{research_context}' not sufficient"
        
        return True, "All knowledge requirements met"
    
    def is_language_talent(self):
        """Check if this is a language talent"""
        return self.knowledge_type == 'language'
    
    def get_language_difficulty(self):
        """Get language difficulty (only for language talents)"""
        if self.is_language_talent():
            return self.language_difficulty
        return None
    
    def get_script_required(self):
        """Get required script (only for language talents)"""
        if self.is_language_talent():
            return self.script_required
        return None 