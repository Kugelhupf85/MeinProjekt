"""
Tests for Character Services
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.characters.models import (
    Character, CharacterRuleSetData, RuleSet, DSARace, DSACulture, DSAProfession,
    DSAAdvantage, DSADisadvantage
)
from apps.characters.services.character_calculation_engine import CharacterCalculationEngine
from apps.characters.services.character_crud import CharacterCRUDService
from apps.world.models import World

User = get_user_model()


class CharacterCalculationEngineTest(TestCase):
    """Tests für CharacterCalculationEngine"""
    
    def setUp(self):
        """Set up test data"""
        self.core_attributes = {
            'MU': 14, 'KL': 13, 'IN': 12, 'CH': 11,
            'FF': 10, 'GE': 9, 'KO': 8, 'KK': 8
        }
        
        self.race_modifiers = {
            'LE': 5, 'AU': -2
        }
        
        self.advantages = [
            {
                'effects': {'life_points_bonus': 7}
            },
            {
                'effects': {'life_points_penalty': -3}
            }
        ]
    
    def test_calculate_derived_values_basic(self):
        """Test Basis-Berechnung abgeleiteter Werte"""
        derived = CharacterCalculationEngine.calculate_derived_values(self.core_attributes)
        
        # LE = (KO * 2) + KK + 6 = (8 * 2) + 8 + 6 = 30
        self.assertEqual(derived['LE'], 30)
        
        # AU = (KO * 2) + GE + 6 = (8 * 2) + 9 + 6 = 31
        self.assertEqual(derived['AU'], 31)
        
        # MR = (MU + KL + KO) // 5 = (14 + 13 + 8) // 5 = 7
        self.assertEqual(derived['MR'], 7)
        
        # INI = (MU + GE) // 2 = (14 + 9) // 2 = 11
        self.assertEqual(derived['INI'], 11)
    
    def test_calculate_derived_values_with_race_modifiers(self):
        """Test Berechnung mit Rassen-Modifikatoren"""
        derived = CharacterCalculationEngine.calculate_derived_values(
            self.core_attributes, 
            race_modifiers=self.race_modifiers
        )
        
        # LE = 30 + 5 = 35
        self.assertEqual(derived['LE'], 35)
        
        # AU = 31 - 2 = 29
        self.assertEqual(derived['AU'], 29)
    
    def test_calculate_derived_values_with_advantages(self):
        """Test Berechnung mit Vorteilen"""
        derived = CharacterCalculationEngine.calculate_derived_values(
            self.core_attributes,
            advantages=self.advantages
        )
        
        # LE = 30 + 7 - 3 = 34
        self.assertEqual(derived['LE'], 34)
    
    def test_validate_character_rules_valid(self):
        """Test Validierung gültiger Character-Daten"""
        character_data = {
            'core_attributes': self.core_attributes,
            'generation_data': {
                'attribute_maximum': 14,
                'generation_points_max': 110
            },
            'advantages': [],
            'disadvantages': []
        }
        
        errors = CharacterCalculationEngine.validate_character_rules(character_data)
        self.assertEqual(len(errors), 0)
    
    def test_validate_character_rules_invalid_attributes(self):
        """Test Validierung ungültiger Attribute"""
        invalid_attributes = self.core_attributes.copy()
        invalid_attributes['MU'] = 25  # Above maximum
        
        character_data = {
            'core_attributes': invalid_attributes,
            'generation_data': {
                'attribute_maximum': 14,
                'generation_points_max': 110
            },
            'advantages': [],
            'disadvantages': []
        }
        
        errors = CharacterCalculationEngine.validate_character_rules(character_data)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('MU' in error for error in errors))
    
    def test_validate_character_rules_incompatible_advantages(self):
        """Test Validierung inkompatibler Vorteile"""
        character_data = {
            'core_attributes': self.core_attributes,
            'generation_data': {
                'attribute_maximum': 14,
                'generation_points_max': 110
            },
            'advantages': [
                {'name': 'Glück', 'incompatible_with': ['Pech']},
                {'name': 'Pech', 'incompatible_with': ['Glück']}
            ],
            'disadvantages': []
        }
        
        errors = CharacterCalculationEngine.validate_character_rules(character_data)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('inkompatibel' in error for error in errors))
    
    def test_calculate_generation_points(self):
        """Test Generierungspunkte-Berechnung"""
        character_data = {
            'core_attributes': self.core_attributes,
            'advantages': [
                {'level': 1, 'gp_cost_base': 10, 'gp_cost_per_level': 0},
                {'level': 2, 'gp_cost_base': 15, 'gp_cost_per_level': 5}
            ],
            'disadvantages': [
                {'level': 1, 'gp_gain_base': 5, 'gp_gain_per_level': 0}
            ]
        }
        
        gp_data = CharacterCalculationEngine.calculate_generation_points(character_data)
        
        # Attribute points: 85 - 64 = 21
        self.assertEqual(gp_data['attribute_points_used'], 21)
        
        # Advantage points: 10 + (15 + 5) = 30
        self.assertEqual(gp_data['advantage_points_used'], 30)
        
        # Disadvantage points gained: 5
        self.assertEqual(gp_data['disadvantage_points_gained'], 5)
        
        # Total: 21 + 30 - 5 = 46
        self.assertEqual(gp_data['total_points_used'], 46)
        
        # Remaining: 110 - 46 = 64
        self.assertEqual(gp_data['points_remaining'], 64)
    
    def test_apply_race_modifiers(self):
        """Test Rassen-Modifikatoren-Anwendung"""
        base_attributes = {'MU': 10, 'KL': 10, 'IN': 10}
        race_modifiers = {'MU': 1, 'KL': -1}
        
        modified = CharacterCalculationEngine.apply_race_modifiers(base_attributes, race_modifiers)
        
        self.assertEqual(modified['MU'], 11)  # +1
        self.assertEqual(modified['KL'], 9)   # -1
        self.assertEqual(modified['IN'], 10)  # unchanged
    
    def test_apply_culture_bonuses(self):
        """Test Kultur-Boni-Anwendung"""
        talents = {'Reiten': 5, 'Schwimmen': 3}
        culture_bonuses = {'Reiten': 2, 'Singen': 1}
        
        modified = CharacterCalculationEngine.apply_culture_bonuses(talents, culture_bonuses)
        
        self.assertEqual(modified['Reiten'], 7)   # 5 + 2
        self.assertEqual(modified['Schwimmen'], 3) # unchanged
        # Note: apply_culture_bonuses only modifies existing talents, doesn't add new ones
        # So 'Singen' won't be in the result
    
    def test_validate_profession_requirements_valid(self):
        """Test Profession-Anforderungs-Validierung (gültig)"""
        attributes = {'MU': 13, 'KL': 11, 'IN': 12}
        requirements = {'MU': 13, 'KL': 11}
        
        is_valid, message = CharacterCalculationEngine.validate_profession_requirements(
            attributes, requirements
        )
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "Alle Anforderungen erfüllt")
    
    def test_validate_profession_requirements_invalid(self):
        """Test Profession-Anforderungs-Validierung (ungültig)"""
        attributes = {'MU': 12, 'KL': 11, 'IN': 12}
        requirements = {'MU': 13, 'KL': 11}
        
        is_valid, message = CharacterCalculationEngine.validate_profession_requirements(
            attributes, requirements
        )
        
        self.assertFalse(is_valid)
        self.assertIn('MU', message)
    
    def test_calculate_talent_check(self):
        """Test Talent-Probe-Berechnung"""
        talent_value = 10
        governing_attributes = [14, 13, 12]  # MU, KL, IN
        difficulty = 'B'
        
        result = CharacterCalculationEngine.calculate_talent_check(
            talent_value, governing_attributes, difficulty
        )
        
        self.assertEqual(result['talent_value'], 10)
        self.assertEqual(result['avg_attributes'], 13)  # (14+13+12)/3
        self.assertEqual(result['difficulty_factor'], 2)  # B = 2
        self.assertEqual(result['probe_value'], 23)  # 10 + 13
        self.assertEqual(result['difficulty'], 'B')


class CharacterCRUDServiceTest(TestCase):
    """Tests für CharacterCRUDService"""
    
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
        
        self.race = DSARace.objects.create(
            name='Mensch',
            attribute_modifiers={},
            description='Test race'
        )
        
        self.culture = DSACulture.objects.create(
            name='Mittelreich',
            description='Test culture'
        )
        
        self.profession = DSAProfession.objects.create(
            name='Krieger',
            category='combat',
            description='Test profession'
        )
        
        self.advantage = DSAAdvantage.objects.create(
            name='Glück',
            gp_cost_base=10,
            max_levels=1,
            effects={},
            incompatible_with=[],
            description='Test advantage'
        )
        
        self.disadvantage = DSADisadvantage.objects.create(
            name='Pech',
            gp_gain_base=10,
            max_levels=1,
            effects={},
            incompatible_with=[],
            description='Test disadvantage'
        )
    
    def test_create_character_success(self):
        """Test erfolgreiche Character-Erstellung"""
        character_data = {
            'name': 'Test Character',
            'rule_set': 'dsa_4_1',
            'core_attributes': {
                'MU': 14, 'KL': 13, 'IN': 12, 'CH': 11,
                'FF': 10, 'GE': 9, 'KO': 8, 'KK': 8
            },
            'generation_points_max': 110,
            'attribute_maximum': 14,
            'advantages': [
                {'name': 'Glück', 'level': 1}
            ],
            'disadvantages': [
                {'name': 'Pech', 'level': 1}
            ]
        }
        
        character, errors = CharacterCRUDService.create_character(
            user=self.user,
            world_id=str(self.world.id),
            character_data=character_data
        )
        
        if character is None:
            print(f"Errors: {errors}")
        self.assertIsNotNone(character)
        if len(errors) > 0:
            print(f"Validation errors: {errors}")
        self.assertEqual(len(errors), 0)
        self.assertEqual(character.name, 'Test Character')
        self.assertEqual(character.user, self.user)
        self.assertEqual(character.world, self.world)
        self.assertEqual(character.rule_set, self.rule_set)
        
        # Check if CharacterRuleSetData was created
        self.assertTrue(hasattr(character, 'ruleset_data'))
        self.assertEqual(character.ruleset_data.generation_points_max, 110)
        
        # Check if advantages were created
        self.assertEqual(character.character_advantages.count(), 1)
        self.assertEqual(character.character_advantages.first().advantage, self.advantage)
        
        # Check if disadvantages were created
        self.assertEqual(character.character_disadvantages.count(), 1)
        self.assertEqual(character.character_disadvantages.first().disadvantage, self.disadvantage)
    
    def test_create_character_invalid_advantage(self):
        """Test Character-Erstellung mit ungültigem Vorteil"""
        character_data = {
            'name': 'Test Character',
            'rule_set': 'dsa_4_1',
            'core_attributes': {
                'MU': 14, 'KL': 13, 'IN': 12, 'CH': 11,
                'FF': 10, 'GE': 9, 'KO': 8, 'KK': 7
            },
            'advantages': [
                {'name': 'NichtexistenterVorteil', 'level': 1}
            ]
        }
        
        character, errors = CharacterCRUDService.create_character(
            user=self.user,
            world_id=str(self.world.id),
            character_data=character_data
        )
        
        self.assertIsNone(character)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('NichtexistenterVorteil' in error for error in errors))
    
    def test_get_character_success(self):
        """Test erfolgreicher Character-Abruf"""
        character = Character.objects.create(
            user=self.user,
            world=self.world,
            rule_set=self.rule_set,
            name='Test Character',
            core_attributes={'MU': 14, 'KL': 13, 'IN': 12, 'CH': 11, 'FF': 10, 'GE': 9, 'KO': 8, 'KK': 7}
        )
        
        retrieved_character = CharacterCRUDService.get_character(
            character_id=str(character.id),
            user=self.user
        )
        
        self.assertIsNotNone(retrieved_character)
        self.assertEqual(retrieved_character, character)
    
    def test_get_character_not_found(self):
        """Test Character-Abruf für nicht existierenden Character"""
        import uuid
        
        retrieved_character = CharacterCRUDService.get_character(
            character_id=str(uuid.uuid4()),
            user=self.user
        )
        
        self.assertIsNone(retrieved_character)
    
    def test_get_user_characters(self):
        """Test User-Charaktere-Abruf"""
        # Create multiple characters
        character1 = Character.objects.create(
            user=self.user,
            world=self.world,
            rule_set=self.rule_set,
            name='Character 1',
            core_attributes={'MU': 14, 'KL': 13, 'IN': 12, 'CH': 11, 'FF': 10, 'GE': 9, 'KO': 8, 'KK': 7}
        )
        
        character2 = Character.objects.create(
            user=self.user,
            world=self.world,
            rule_set=self.rule_set,
            name='Character 2',
            core_attributes={'MU': 13, 'KL': 14, 'IN': 11, 'CH': 12, 'FF': 9, 'GE': 10, 'KO': 7, 'KK': 8}
        )
        
        # Test without world filter
        characters = CharacterCRUDService.get_user_characters(user=self.user)
        self.assertEqual(len(characters), 2)
        
        # Test with world filter
        characters = CharacterCRUDService.get_user_characters(
            user=self.user,
            world_id=str(self.world.id)
        )
        self.assertEqual(len(characters), 2)
    
    def test_get_reference_data(self):
        """Test Referenz-Daten-Abruf"""
        reference_data = CharacterCRUDService.get_reference_data()
        
        self.assertIn('races', reference_data)
        self.assertIn('cultures', reference_data)
        self.assertIn('professions', reference_data)
        self.assertIn('advantages', reference_data)
        self.assertIn('disadvantages', reference_data)
        
        # Check if our test data is included
        race_names = [race['name'] for race in reference_data['races']]
        self.assertIn('Mensch', race_names)
        
        culture_names = [culture['name'] for culture in reference_data['cultures']]
        self.assertIn('Mittelreich', culture_names)
        
        profession_names = [prof['name'] for prof in reference_data['professions']]
        self.assertIn('Krieger', profession_names)
        
        advantage_names = [adv['name'] for adv in reference_data['advantages']]
        self.assertIn('Glück', advantage_names)
        
        disadvantage_names = [dis['name'] for dis in reference_data['disadvantages']]
        self.assertIn('Pech', disadvantage_names) 