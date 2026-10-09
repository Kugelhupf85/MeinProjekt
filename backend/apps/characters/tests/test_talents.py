"""
Tests for DSA Talent Models
"""

from django.test import TestCase
from django.core.exceptions import ValidationError

from apps.characters.models import (
    DSATalentCombat, DSATalentSocial, DSATalentKnowledge, DSATalentPhysical
)


class DSATalentCombatTest(TestCase):
    """Tests für DSATalentCombat-Model"""
    
    def setUp(self):
        """Set up test data"""
        self.combat_talent = DSATalentCombat.objects.create(
            name='Schwerter',
            governing_attributes=['FF', 'GE'],
            improvement_factor='B',
            untrained_use=True,
            untrained_penalty=3,
            talent_category='Kampf',
            requirements={'minimum_FF': 12},
            restrictions={'weapon_type': 'sword'},
            special_rules={'can_parry': True},
            description='Kampf mit Schwertern',
            combat_type='melee',
            applicable_weapons=['Schwert', 'Anderthalbhänder', 'Säbel'],
            combat_bonuses={'parry_bonus': 1},
            combat_rules={'can_parry_ranged': False},
            combat_requirements={'weapon_requirements': ['sword']}
        )
    
    def test_combat_talent_creation(self):
        """Test Combat Talent Erstellung"""
        self.assertEqual(self.combat_talent.name, 'Schwerter')
        self.assertEqual(self.combat_talent.combat_type, 'melee')
        self.assertIn('FF', self.combat_talent.governing_attributes)
        self.assertEqual(self.combat_talent.improvement_factor, 'B')
    
    def test_combat_talent_str(self):
        """Test String-Repräsentation"""
        self.assertEqual(str(self.combat_talent), 'Schwerter (Nahkampf)')
    
    def test_is_applicable_to_weapon(self):
        """Test Waffen-Anwendbarkeit"""
        self.assertTrue(self.combat_talent.is_applicable_to_weapon('Schwert'))
        self.assertTrue(self.combat_talent.is_applicable_to_weapon('Anderthalbhänder'))
        self.assertFalse(self.combat_talent.is_applicable_to_weapon('Axt'))
    
    def test_get_combat_bonus(self):
        """Test Kampf-Bonus-Abruf"""
        self.assertEqual(self.combat_talent.get_combat_bonus('parry_bonus'), 1)
        self.assertEqual(self.combat_talent.get_combat_bonus('nonexistent'), 0)
    
    def test_get_combat_rule(self):
        """Test Kampf-Regel-Abruf"""
        self.assertFalse(self.combat_talent.get_combat_rule('can_parry_ranged'))
        self.assertIsNone(self.combat_talent.get_combat_rule('nonexistent'))
    
    def test_check_combat_requirements(self):
        """Test Kampf-Anforderungs-Prüfung"""
        character_data = {'FF': 15}
        weapon_data = {'category': 'sword'}
        armor_data = {'type': 'light'}
        
        result, message = self.combat_talent.check_combat_requirements(
            character_data, weapon_data, armor_data
        )
        self.assertTrue(result)
        
        weapon_data = {'category': 'axe'}
        result, message = self.combat_talent.check_combat_requirements(
            character_data, weapon_data, armor_data
        )
        self.assertFalse(result)


class DSATalentSocialTest(TestCase):
    """Tests für DSATalentSocial-Model"""
    
    def setUp(self):
        """Set up test data"""
        self.social_talent = DSATalentSocial.objects.create(
            name='Überzeugen',
            governing_attributes=['CH', 'KL'],
            improvement_factor='C',
            untrained_use=False,
            untrained_penalty=5,
            talent_category='Sozial',
            requirements={'minimum_CH': 10},
            restrictions={'social_context': 'formal'},
            special_rules={'can_influence_groups': True},
            description='Überzeugungskraft in sozialen Situationen',
            social_type='influence',
            social_contexts=['negotiation', 'diplomacy', 'sales'],
            social_bonuses={'reputation_bonus': 1},
            social_rules={'requires_eye_contact': True},
            social_requirements={'minimum_audience_size': 1}
        )
    
    def test_social_talent_creation(self):
        """Test Social Talent Erstellung"""
        self.assertEqual(self.social_talent.name, 'Überzeugen')
        self.assertEqual(self.social_talent.social_type, 'influence')
        self.assertIn('CH', self.social_talent.governing_attributes)
        self.assertFalse(self.social_talent.untrained_use)
    
    def test_social_talent_str(self):
        """Test String-Repräsentation"""
        self.assertEqual(str(self.social_talent), 'Überzeugen (Einflussnahme)')
    
    def test_is_applicable_in_context(self):
        """Test Kontext-Anwendbarkeit"""
        self.assertTrue(self.social_talent.is_applicable_in_context('negotiation'))
        self.assertTrue(self.social_talent.is_applicable_in_context('diplomacy'))
        self.assertFalse(self.social_talent.is_applicable_in_context('combat'))
    
    def test_get_social_bonus(self):
        """Test Sozial-Bonus-Abruf"""
        self.assertEqual(self.social_talent.get_social_bonus('reputation_bonus'), 1)
        self.assertEqual(self.social_talent.get_social_bonus('nonexistent'), 0)


class DSATalentKnowledgeTest(TestCase):
    """Tests für DSATalentKnowledge-Model"""
    
    def setUp(self):
        """Set up test data"""
        self.knowledge_talent = DSATalentKnowledge.objects.create(
            name='Geschichtswissen',
            governing_attributes=['KL', 'IN'],
            improvement_factor='D',
            untrained_use=True,
            untrained_penalty=2,
            talent_category='Wissen',
            requirements={'minimum_KL': 11},
            restrictions={'knowledge_domain': 'history'},
            special_rules={'can_teach': True},
            description='Wissen über historische Ereignisse',
            knowledge_type='academic',
            knowledge_domains=['ancient_history', 'recent_history', 'legends'],
            knowledge_bonuses={'research_bonus': 1},
            knowledge_rules={'requires_library_access': False},
            knowledge_requirements={'minimum_study_time': 1},
            language_difficulty='',
            script_required=''
        )
    
    def test_knowledge_talent_creation(self):
        """Test Knowledge Talent Erstellung"""
        self.assertEqual(self.knowledge_talent.name, 'Geschichtswissen')
        self.assertEqual(self.knowledge_talent.knowledge_type, 'academic')
        self.assertIn('KL', self.knowledge_talent.governing_attributes)
    
    def test_knowledge_talent_str(self):
        """Test String-Repräsentation"""
        self.assertEqual(str(self.knowledge_talent), 'Geschichtswissen (Akademisch)')
    
    def test_is_applicable_to_domain(self):
        """Test Domänen-Anwendbarkeit"""
        self.assertTrue(self.knowledge_talent.is_applicable_to_domain('ancient_history'))
        self.assertTrue(self.knowledge_talent.is_applicable_to_domain('recent_history'))
        self.assertFalse(self.knowledge_talent.is_applicable_to_domain('magic'))
    
    def test_get_knowledge_bonus(self):
        """Test Wissen-Bonus-Abruf"""
        self.assertEqual(self.knowledge_talent.get_knowledge_bonus('research_bonus'), 1)
        self.assertEqual(self.knowledge_talent.get_knowledge_bonus('nonexistent'), 0)


class DSATalentPhysicalTest(TestCase):
    """Tests für DSATalentPhysical-Model"""
    
    def setUp(self):
        """Set up test data"""
        self.physical_talent = DSATalentPhysical.objects.create(
            name='Klettern',
            governing_attributes=['GE', 'KK'],
            improvement_factor='B',
            untrained_use=True,
            untrained_penalty=3,
            talent_category='Körperlich',
            requirements={'minimum_GE': 10},
            restrictions={'surface_type': 'climbable'},
            special_rules={'can_climb_smooth_surfaces': False},
            description='Klettern an verschiedenen Oberflächen',
            physical_type='movement',
            physical_contexts=['climbing', 'mountaineering', 'urban_climbing'],
            physical_bonuses={'height_bonus': 2},
            physical_rules={'requires_hands_free': True},
            physical_requirements={'minimum_strength': 8},
            environmental_modifiers={'wet_surface': -2, 'icy_surface': -4}
        )
    
    def test_physical_talent_creation(self):
        """Test Physical Talent Erstellung"""
        self.assertEqual(self.physical_talent.name, 'Klettern')
        self.assertEqual(self.physical_talent.physical_type, 'movement')
        self.assertIn('GE', self.physical_talent.governing_attributes)
    
    def test_physical_talent_str(self):
        """Test String-Repräsentation"""
        self.assertEqual(str(self.physical_talent), 'Klettern (Bewegung)')
    
    def test_is_applicable_in_context(self):
        """Test Kontext-Anwendbarkeit"""
        self.assertTrue(self.physical_talent.is_applicable_in_context('climbing'))
        self.assertTrue(self.physical_talent.is_applicable_in_context('mountaineering'))
        self.assertFalse(self.physical_talent.is_applicable_in_context('swimming'))
    
    def test_get_environmental_modifier(self):
        """Test Umwelt-Modifikator-Abruf"""
        self.assertEqual(self.physical_talent.get_environmental_modifier('wet_surface'), -2)
        self.assertEqual(self.physical_talent.get_environmental_modifier('icy_surface'), -4)
        self.assertEqual(self.physical_talent.get_environmental_modifier('nonexistent'), 0)
    
    def test_get_physical_bonus(self):
        """Test Körperlich-Bonus-Abruf"""
        self.assertEqual(self.physical_talent.get_physical_bonus('height_bonus'), 2)
        self.assertEqual(self.physical_talent.get_physical_bonus('nonexistent'), 0) 