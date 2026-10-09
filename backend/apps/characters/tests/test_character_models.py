"""
Tests for Character Models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.characters.models import (
    Character, CharacterRuleSetData, RuleSet, DSARace, DSACulture, DSAProfession,
    DSAAdvantage, DSADisadvantage, CharacterAdvantage, CharacterDisadvantage
)
from apps.world.models import World

User = get_user_model()


class RuleSetModelTest(TestCase):
    """Tests für RuleSet-Model"""
    
    def setUp(self):
        """Set up test data"""
        self.rule_set = RuleSet.objects.create(
            name='dsa_4_1',
            display_name='DSA 4.1',
            version='4.1',
            attribute_schema={
                'required': ['MU', 'KL', 'IN', 'CH', 'FF', 'GE', 'KO', 'KK'],
                'properties': {
                    'MU': {'type': 'integer', 'minimum': 8, 'maximum': 20}
                }
            },
            default_values={
                'generation_points_max': 110,
                'attribute_maximum': 14
            }
        )
    
    def test_rule_set_creation(self):
        """Test RuleSet-Erstellung"""
        self.assertEqual(self.rule_set.name, 'dsa_4_1')
        self.assertEqual(self.rule_set.display_name, 'DSA 4.1')
        self.assertEqual(self.rule_set.version, '4.1')
        self.assertTrue(self.rule_set.is_active)
    
    def test_rule_set_str(self):
        """Test RuleSet String-Repräsentation"""
        self.assertEqual(str(self.rule_set), 'DSA 4.1 (4.1)')
    
    def test_get_attribute_schema(self):
        """Test Attribute-Schema-Abruf"""
        schema = self.rule_set.get_attribute_schema()
        self.assertIn('required', schema)
        self.assertIn('properties', schema)
    
    def test_get_default_values(self):
        """Test Default-Werte-Abruf"""
        defaults = self.rule_set.get_default_values()
        self.assertEqual(defaults['generation_points_max'], 110)
        self.assertEqual(defaults['attribute_maximum'], 14)


class CharacterModelTest(TestCase):
    """Tests für Character-Model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.world = World.objects.create(
            name='Test World',
            description='Test World Description',
            created_by=self.user
        )
        
        self.rule_set = RuleSet.objects.create(
            name='dsa_4_1',
            display_name='DSA 4.1',
            version='4.1',
            attribute_schema={
                'required': ['MU', 'KL', 'IN', 'CH', 'FF', 'GE', 'KO', 'KK']
            }
        )
        
        self.character = Character.objects.create(
            user=self.user,
            world=self.world,
            rule_set=self.rule_set,
            name='Test Character',
            core_attributes={
                'MU': 14, 'KL': 13, 'IN': 12, 'CH': 11,
                'FF': 10, 'GE': 9, 'KO': 8, 'KK': 7
            }
        )
    
    def test_character_creation(self):
        """Test Character-Erstellung"""
        self.assertEqual(self.character.name, 'Test Character')
        self.assertEqual(self.character.user, self.user)
        self.assertEqual(self.character.world, self.world)
        self.assertEqual(self.character.rule_set, self.rule_set)
        self.assertEqual(self.character.status, 'draft')
    
    def test_character_str(self):
        """Test Character String-Repräsentation"""
        self.assertEqual(str(self.character), 'Test Character (DSA 4.1)')
    
    def test_character_status_properties(self):
        """Test Character-Status-Properties"""
        self.assertTrue(self.character.is_draft)
        self.assertFalse(self.character.is_active)
        self.assertFalse(self.character.is_archived)
        
        self.character.activate()
        self.assertTrue(self.character.is_active)
        self.assertFalse(self.character.is_draft)
        
        self.character.archive()
        self.assertTrue(self.character.is_archived)
        self.assertFalse(self.character.is_active)
    
    def test_get_core_attribute(self):
        """Test Core-Attribute-Abruf"""
        self.assertEqual(self.character.get_core_attribute('MU'), 14)
        self.assertEqual(self.character.get_core_attribute('KL'), 13)
        self.assertIsNone(self.character.get_core_attribute('NONEXISTENT'))
    
    def test_set_core_attribute(self):
        """Test Core-Attribute-Setzung"""
        self.character.set_core_attribute('MU', 15)
        self.assertEqual(self.character.get_core_attribute('MU'), 15)
    
    def test_character_validation(self):
        """Test Character-Validierung"""
        # Valid character should not raise validation error
        self.character.full_clean()
        
        # Invalid character should raise validation error
        invalid_character = Character(
            user=self.user,
            world=self.world,
            rule_set=self.rule_set,
            name='Invalid Character',
            core_attributes={'MU': 25}  # Above maximum
        )
        
        with self.assertRaises(ValidationError):
            invalid_character.full_clean()


class CharacterRuleSetDataModelTest(TestCase):
    """Tests für CharacterRuleSetData-Model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.world = World.objects.create(
            name='Test World',
            description='Test World Description',
            created_by=self.user
        )
        
        self.rule_set = RuleSet.objects.create(
            name='dsa_4_1',
            display_name='DSA 4.1',
            version='4.1'
        )
        
        self.character = Character.objects.create(
            user=self.user,
            world=self.world,
            rule_set=self.rule_set,
            name='Test Character',
            core_attributes={
                'MU': 14, 'KL': 13, 'IN': 12, 'CH': 11,
                'FF': 10, 'GE': 9, 'KO': 8, 'KK': 7
            }
        )
        
        self.ruleset_data = CharacterRuleSetData.objects.create(
            character=self.character,
            generation_points_max=110,
            attribute_maximum=14,
            xp_total=0,
            level=1
        )
    
    def test_ruleset_data_creation(self):
        """Test CharacterRuleSetData-Erstellung"""
        self.assertEqual(self.ruleset_data.character, self.character)
        self.assertEqual(self.ruleset_data.generation_points_max, 110)
        self.assertEqual(self.ruleset_data.attribute_maximum, 14)
        self.assertEqual(self.ruleset_data.xp_total, 0)
        self.assertEqual(self.ruleset_data.level, 1)
    
    def test_ruleset_data_str(self):
        """Test CharacterRuleSetData String-Repräsentation"""
        self.assertEqual(str(self.ruleset_data), 'Data for Test Character')
    
    def test_calculate_derived_values(self):
        """Test abgeleitete Werte-Berechnung"""
        self.ruleset_data.calculate_derived_values()
        
        # Test calculated values based on core attributes
        # LE = (KO * 2) + KK + 6 = (8 * 2) + 7 + 6 = 29
        self.assertEqual(self.ruleset_data.life_energy, 29)
        
        # AU = (KO * 2) + GE + 6 = (8 * 2) + 9 + 6 = 31
        self.assertEqual(self.ruleset_data.endurance, 31)
        
        # MR = (MU + KL + KO) // 5 = (14 + 13 + 8) // 5 = 7
        self.assertEqual(self.ruleset_data.magic_resistance, 7)
    
    def test_generation_points_calculation(self):
        """Test Generierungspunkte-Berechnung"""
        # Base cost: 8 points per attribute (8 * 8 = 64)
        # Total attributes: 14+13+12+11+10+9+8+7 = 84
        # Used points: 84 - 64 = 20
        self.assertEqual(self.ruleset_data.generation_points_used, 20)
        self.assertEqual(self.ruleset_data.generation_points_remaining, 90)  # 110 - 20
        self.assertTrue(self.ruleset_data.is_generation_valid)


class DSARaceModelTest(TestCase):
    """Tests für DSA Race-Model"""
    
    def setUp(self):
        """Set up test data"""
        self.race = DSARace.objects.create(
            name='Elf',
            attribute_modifiers={
                'MU': 0, 'KL': 1, 'IN': 0, 'CH': 0,
                'FF': 1, 'GE': 0, 'KO': -1, 'KK': 0
            },
            granted_special_abilities=['Infrarotsicht'],
            starting_modifications={
                'life_points': -5,
                'astral_energy': 5
            },
            generation_point_cost=0,
            description='Die Elfen sind eine alte, magiebegabte Rasse.'
        )
    
    def test_race_creation(self):
        """Test Race-Erstellung"""
        self.assertEqual(self.race.name, 'Elf')
        self.assertEqual(self.race.generation_point_cost, 0)
        self.assertTrue(self.race.is_active)
    
    def test_race_str(self):
        """Test Race String-Repräsentation"""
        self.assertEqual(str(self.race), 'Elf')
    
    def test_get_attribute_modifier(self):
        """Test Attributs-Modifikator-Abruf"""
        self.assertEqual(self.race.get_attribute_modifier('KL'), 1)
        self.assertEqual(self.race.get_attribute_modifier('KO'), -1)
        self.assertEqual(self.race.get_attribute_modifier('NONEXISTENT'), 0)
    
    def test_has_special_ability(self):
        """Test Special-Ability-Check"""
        self.assertTrue(self.race.has_special_ability('Infrarotsicht'))
        self.assertFalse(self.race.has_special_ability('NichtexistenteFähigkeit'))
    
    def test_apply_to_attributes(self):
        """Test Attributs-Modifikation"""
        base_attributes = {
            'MU': 10, 'KL': 10, 'IN': 10, 'CH': 10,
            'FF': 10, 'GE': 10, 'KO': 10, 'KK': 10
        }
        
        modified_attributes = self.race.apply_to_attributes(base_attributes)
        
        self.assertEqual(modified_attributes['KL'], 11)  # +1
        self.assertEqual(modified_attributes['FF'], 11)  # +1
        self.assertEqual(modified_attributes['KO'], 9)   # -1
        self.assertEqual(modified_attributes['MU'], 10)  # unchanged


class DSAAdvantageModelTest(TestCase):
    """Tests für DSA Advantage-Model"""
    
    def setUp(self):
        """Set up test data"""
        self.advantage = DSAAdvantage.objects.create(
            name='Glück',
            gp_cost_base=10,
            gp_cost_per_level=5,
            max_levels=3,
            requirements={},
            effects={'schips_per_session': 2},
            incompatible_with=['Pech'],
            category='general',
            scaling_effects={'schips_per_session_per_level': 1},
            description='Der Charakter hat mehr Glück als andere.'
        )
    
    def test_advantage_creation(self):
        """Test Advantage-Erstellung"""
        self.assertEqual(self.advantage.name, 'Glück')
        self.assertEqual(self.advantage.gp_cost_base, 10)
        self.assertEqual(self.advantage.max_levels, 3)
        self.assertEqual(self.advantage.category, 'general')
    
    def test_advantage_str(self):
        """Test Advantage String-Repräsentation"""
        self.assertEqual(str(self.advantage), 'Glück')
    
    def test_get_gp_cost(self):
        """Test GP-Cost-Berechnung"""
        self.assertEqual(self.advantage.get_gp_cost(1), 10)  # base cost
        self.assertEqual(self.advantage.get_gp_cost(2), 15)  # base + per_level
        self.assertEqual(self.advantage.get_gp_cost(3), 20)  # base + 2*per_level
    
    def test_get_effect(self):
        """Test Effect-Berechnung"""
        self.assertEqual(self.advantage.get_effect('schips_per_session', 1), 2)  # base effect
        self.assertEqual(self.advantage.get_effect('schips_per_session', 2), 3)  # base + scaling
        self.assertEqual(self.advantage.get_effect('schips_per_session', 3), 4)  # base + 2*scaling
    
    def test_is_incompatible_with(self):
        """Test Inkompatibilitäts-Check"""
        self.assertTrue(self.advantage.is_incompatible_with('Pech'))
        self.assertFalse(self.advantage.is_incompatible_with('AndererVorteil'))
    
    def test_is_scalable(self):
        """Test Scalability-Check"""
        self.assertTrue(self.advantage.is_scalable())  # max_levels > 1
        
        non_scalable = DSAAdvantage.objects.create(
            name='Einfacher Vorteil',
            gp_cost_base=5,
            max_levels=1
        )
        self.assertFalse(non_scalable.is_scalable())  # max_levels = 1
    
    def test_get_total_gp_cost(self):
        """Test Total GP-Cost-Berechnung"""
        # Level 1: 10, Level 2: 15, Level 3: 20 = 45 total
        self.assertEqual(self.advantage.get_total_gp_cost(), 45)


class CharacterAdvantageModelTest(TestCase):
    """Tests für Character-Advantage-Verbindung"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.world = World.objects.create(
            name='Test World',
            description='Test World Description',
            created_by=self.user
        )
        
        self.rule_set = RuleSet.objects.create(
            name='dsa_4_1',
            display_name='DSA 4.1',
            version='4.1'
        )
        
        self.character = Character.objects.create(
            user=self.user,
            world=self.world,
            rule_set=self.rule_set,
            name='Test Character',
            core_attributes={'MU': 14, 'KL': 13, 'IN': 12, 'CH': 11, 'FF': 10, 'GE': 9, 'KO': 8, 'KK': 7}
        )
        
        self.advantage = DSAAdvantage.objects.create(
            name='Glück',
            gp_cost_base=10,
            gp_cost_per_level=5,
            max_levels=3,
            effects={'schips_per_session': 2},
            description='Test advantage'
        )
        
        self.character_advantage = CharacterAdvantage.objects.create(
            character=self.character,
            advantage=self.advantage,
            level=2,
            custom_modifiers={'bonus_effect': 1}
        )
    
    def test_character_advantage_creation(self):
        """Test CharacterAdvantage-Erstellung"""
        self.assertEqual(self.character_advantage.character, self.character)
        self.assertEqual(self.character_advantage.advantage, self.advantage)
        self.assertEqual(self.character_advantage.level, 2)
        self.assertTrue(self.character_advantage.is_valid)
    
    def test_character_advantage_str(self):
        """Test CharacterAdvantage String-Repräsentation"""
        self.assertEqual(str(self.character_advantage), 'Test Character - Glück (Level 2)')
    
    def test_gp_cost_property(self):
        """Test GP-Cost-Property"""
        self.assertEqual(self.character_advantage.gp_cost, 15)  # 10 + 5
    
    def test_total_effects_property(self):
        """Test Total-Effects-Property"""
        effects = self.character_advantage.total_effects
        self.assertEqual(effects['schips_per_session'], 2)  # base effect
        self.assertEqual(effects['bonus_effect'], 1)  # custom modifier
    
    def test_get_effect(self):
        """Test Effect-Abruf"""
        self.assertEqual(self.character_advantage.get_effect('schips_per_session'), 2)
        self.assertEqual(self.character_advantage.get_effect('bonus_effect'), 1)
        self.assertEqual(self.character_advantage.get_effect('nonexistent'), 0) 