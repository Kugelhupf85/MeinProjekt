"""
Tests for DSA Special Abilities Models
"""

from django.test import TestCase
from django.core.exceptions import ValidationError

from apps.characters.models import (
    DSASpecialAbilityGeneral, DSASpecialAbilityCombat, DSASpecialAbilityMagic,
    DSASpecialAbilityTerrain, DSASpecialAbilityClerical
)


class DSASpecialAbilityGeneralTest(TestCase):
    """Tests für DSASpecialAbilityGeneral-Model"""
    
    def setUp(self):
        """Set up test data"""
        self.special_ability = DSASpecialAbilityGeneral.objects.create(
            name='Kampfreflexe',
            ap_cost_base=5,
            ap_cost_per_level=2,
            max_levels=3,
            category='combat',
            requirements={'attributes': {'FF': 14}},
            effects={'initiative_bonus': 2},
            scaling_effects={'initiative_bonus_per_level': 1},
            incompatible_with=['Schwerfällig'],
            restrictions={'armor_type': 'light'},
            prerequisites={'combat_talent': 'Nahkampf'},
            description='Erhöht die Initiative im Kampf'
        )
    
    def test_special_ability_creation(self):
        """Test Special Ability Erstellung"""
        self.assertEqual(self.special_ability.name, 'Kampfreflexe')
        self.assertEqual(self.special_ability.ap_cost_base, 5)
        self.assertEqual(self.special_ability.max_levels, 3)
        self.assertEqual(self.special_ability.category, 'combat')
    
    def test_special_ability_str(self):
        """Test String-Repräsentation"""
        self.assertEqual(str(self.special_ability), 'Kampfreflexe')
    
    def test_get_total_ap_cost(self):
        """Test AP-Kosten-Berechnung"""
        # Level 1: 5 AP
        self.assertEqual(self.special_ability.get_ap_cost(1), 5)
        # Level 2: 5 + 2 = 7 AP
        self.assertEqual(self.special_ability.get_ap_cost(2), 7)
        # Level 3: 5 + 2*2 = 9 AP
        self.assertEqual(self.special_ability.get_ap_cost(3), 9)
    
    def test_get_effect_value(self):
        """Test Effekt-Wert-Berechnung"""
        # Level 1: 2 Bonus
        self.assertEqual(self.special_ability.get_effect('initiative_bonus', 1), 2)
        # Level 2: 2 + 1 = 3 Bonus
        self.assertEqual(self.special_ability.get_effect('initiative_bonus', 2), 3)
        # Level 3: 2 + 2 = 4 Bonus
        self.assertEqual(self.special_ability.get_effect('initiative_bonus', 3), 4)
    
    def test_check_requirements(self):
        """Test Anforderungs-Prüfung"""
        character_data = {'attributes': {'FF': 15}}
        result, message = self.special_ability.check_requirements(character_data)
        self.assertTrue(result)
        
        character_data = {'attributes': {'FF': 13}}
        result, message = self.special_ability.check_requirements(character_data)
        self.assertFalse(result)
    
    def test_is_incompatible_with(self):
        """Test Inkompatibilitäts-Prüfung"""
        self.assertTrue(self.special_ability.is_incompatible_with('Schwerfällig'))
        self.assertFalse(self.special_ability.is_incompatible_with('Andere Fähigkeit'))


class DSASpecialAbilityCombatTest(TestCase):
    """Tests für DSASpecialAbilityCombat-Model"""
    
    def setUp(self):
        """Set up test data"""
        self.combat_ability = DSASpecialAbilityCombat.objects.create(
            name='Finte',
            combat_type='melee',
            ap_cost_base=3,
            ap_cost_per_level=1,
            max_levels=2,
            applicable_weapons=['Schwerter', 'Säbel'],
            combat_situations=['attack'],
            requirements={'attributes': {'FF': 12}},
            effects={'attack_bonus': 1},
            scaling_effects={'attack_bonus_per_level': 1},
            combat_mechanics={'can_parry_ranged': False},
            description='Verbesserte Angriffe mit bestimmten Waffen'
        )
    
    def test_combat_ability_creation(self):
        """Test Combat Ability Erstellung"""
        self.assertEqual(self.combat_ability.name, 'Finte')
        self.assertEqual(self.combat_ability.combat_type, 'melee')
        self.assertIn('Schwerter', self.combat_ability.applicable_weapons)
    
    def test_is_applicable_to_weapon(self):
        """Test Waffen-Anwendbarkeit"""
        self.assertTrue(self.combat_ability.is_applicable_to_weapon('Schwerter'))
        self.assertTrue(self.combat_ability.is_applicable_to_weapon('Säbel'))
        self.assertFalse(self.combat_ability.is_applicable_to_weapon('Axt'))
    
    def test_get_combat_bonus(self):
        """Test Kampf-Bonus-Berechnung"""
        # Level 1: 1 Bonus
        self.assertEqual(self.combat_ability.get_effect('attack_bonus', 1), 1)
        # Level 2: 1 + 1 = 2 Bonus
        self.assertEqual(self.combat_ability.get_effect('attack_bonus', 2), 2)


class DSASpecialAbilityMagicTest(TestCase):
    """Tests für DSASpecialAbilityMagic-Model"""
    
    def setUp(self):
        """Set up test data"""
        self.magic_ability = DSASpecialAbilityMagic.objects.create(
            name='Merkmalskenntnis',
            magic_type='spell_knowledge',
            ap_cost_base=4,
            ap_cost_per_level=2,
            max_levels=2,
            magic_traditions=['Gildenmagie'],
            affected_categories=['Elementar'],
            affected_spells=['Ignifaxius', 'Fulminictus'],
            requirements={'attributes': {'MU': 13}},
            effects={'spell_difficulty_reduction': 1},
            scaling_effects={'spell_difficulty_reduction_per_level': 1},
            magic_mechanics={'can_modify_spells': True},
            description='Reduziert die Schwierigkeit von Zaubern'
        )
    
    def test_magic_ability_creation(self):
        """Test Magic Ability Erstellung"""
        self.assertEqual(self.magic_ability.name, 'Merkmalskenntnis')
        self.assertEqual(self.magic_ability.magic_type, 'spell_knowledge')
        self.assertIn('Gildenmagie', self.magic_ability.magic_traditions)
    
    def test_affects_spell(self):
        """Test Zauber-Betroffensein"""
        self.assertIn('Ignifaxius', self.magic_ability.affected_spells)
        self.assertIn('Fulminictus', self.magic_ability.affected_spells)
        self.assertNotIn('Balsam Salabunde', self.magic_ability.affected_spells)
    
    def test_affects_category(self):
        """Test Kategorie-Betroffensein"""
        self.assertIn('Elementar', self.magic_ability.affected_categories)
        self.assertNotIn('Heilung', self.magic_ability.affected_categories)


class DSASpecialAbilityTerrainTest(TestCase):
    """Tests für DSASpecialAbilityTerrain-Model"""
    
    def setUp(self):
        """Set up test data"""
        self.terrain_ability = DSASpecialAbilityTerrain.objects.create(
            name='Waldläufer',
            terrain_type='forest',
            ap_cost_base=3,
            ap_cost_per_level=0,
            max_levels=1,
            terrain_bonuses={'navigation_bonus': 2, 'stealth_bonus': 1},
            scaling_bonuses={},
            requirements={},
            effects={'movement_bonus': 1},
            terrain_mechanics={'can_track': True},
            special_features=['animal_empathy'],
            description='Verbesserte Fähigkeiten im Wald'
        )
    
    def test_terrain_ability_creation(self):
        """Test Terrain Ability Erstellung"""
        self.assertEqual(self.terrain_ability.name, 'Waldläufer')
        self.assertEqual(self.terrain_ability.terrain_type, 'forest')
        self.assertIn('navigation_bonus', self.terrain_ability.terrain_bonuses)
    
    def test_get_terrain_bonus(self):
        """Test Gelände-Bonus-Abruf"""
        self.assertEqual(self.terrain_ability.terrain_bonuses.get('navigation_bonus'), 2)
        self.assertEqual(self.terrain_ability.terrain_bonuses.get('stealth_bonus'), 1)
        self.assertEqual(self.terrain_ability.terrain_bonuses.get('nonexistent'), None)


class DSASpecialAbilityClericalTest(TestCase):
    """Tests für DSASpecialAbilityClerical-Model"""
    
    def setUp(self):
        """Set up test data"""
        self.clerical_ability = DSASpecialAbilityClerical.objects.create(
            name='Göttliche Gunst',
            clerical_type='blessing',
            ap_cost_base=5,
            ap_cost_per_level=3,
            max_levels=2,
            deities=['Phex', 'Rondra'],
            liturgy_categories=['Segen', 'Schutz'],
            affected_liturgies=['Balsam Salabunde', 'Schild des Glaubens'],
            requirements={'attributes': {'CH': 12}},
            effects={'liturgy_bonus': 1},
            scaling_effects={'liturgy_bonus_per_level': 1},
            clerical_mechanics={'can_bless_others': True},
            divine_connection_data={'favor_level': 1},
            church_service_requirements={'minimum_service_hours': 10},
            description='Verbesserte liturgische Fähigkeiten'
        )
    
    def test_clerical_ability_creation(self):
        """Test Clerical Ability Erstellung"""
        self.assertEqual(self.clerical_ability.name, 'Göttliche Gunst')
        self.assertEqual(self.clerical_ability.clerical_type, 'blessing')
        self.assertIn('Phex', self.clerical_ability.deities)
    
    def test_affects_deity(self):
        """Test Gottheit-Betroffensein"""
        self.assertIn('Phex', self.clerical_ability.deities)
        self.assertIn('Rondra', self.clerical_ability.deities)
        self.assertNotIn('Boron', self.clerical_ability.deities)
    
    def test_affects_liturgy(self):
        """Test Liturgie-Betroffensein"""
        self.assertIn('Balsam Salabunde', self.clerical_ability.affected_liturgies)
        self.assertIn('Schild des Glaubens', self.clerical_ability.affected_liturgies)
        self.assertNotIn('Andere Liturgie', self.clerical_ability.affected_liturgies) 