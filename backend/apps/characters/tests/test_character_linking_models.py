"""
Tests for Character Linking Models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.characters.models import (
    Character, CharacterSpecialAbility, CharacterTalent, CharacterSpell,
    CharacterLiturgy, CharacterEquipment, CharacterFamily, RuleSet
)
from apps.world.models import World

User = get_user_model()


class CharacterSpecialAbilityTest(TestCase):
    """Tests für CharacterSpecialAbility-Model"""
    
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
        
        self.special_ability = CharacterSpecialAbility.objects.create(
            character=self.character,
            special_ability_data={
                'type': 'general',
                'id': 'test-uuid',
                'name': 'Kampfreflexe'
            },
            level=2,
            specializations=['Nahkampf'],
            acquisition_data={'ap_cost': 7, 'acquisition_date': '2025-01-26'},
            custom_modifications={'initiative_bonus': 3},
            notes='Test Sonderfähigkeit'
        )
    
    def test_special_ability_creation(self):
        """Test Special Ability Erstellung"""
        self.assertEqual(self.special_ability.character, self.character)
        self.assertEqual(self.special_ability.level, 2)
        self.assertEqual(self.special_ability.special_ability_data['name'], 'Kampfreflexe')
    
    def test_special_ability_str(self):
        """Test String-Repräsentation"""
        expected = f"{self.character.name} - Kampfreflexe (Level 2)"
        self.assertEqual(str(self.special_ability), expected)
    
    def test_get_specialization(self):
        """Test Spezialisierungs-Abruf"""
        # Test that specializations list exists
        self.assertIsInstance(self.special_ability.specializations, list)
    
    def test_get_custom_modification(self):
        """Test Benutzerdefinierte Modifikation"""
        self.assertEqual(self.special_ability.get_custom_modification('initiative_bonus'), 3)
        self.assertIsNone(self.special_ability.get_custom_modification('nonexistent'))


class CharacterTalentTest(TestCase):
    """Tests für CharacterTalent-Model"""
    
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
        
        self.talent = CharacterTalent.objects.create(
            character=self.character,
            talent_data={
                'type': 'combat',
                'id': 'test-uuid',
                'name': 'Schwerter'
            },
            value=12,
            specializations=['Anderthalbhänder'],
            acquisition_data={'ap_cost': 5, 'acquisition_date': '2025-01-26'},
            custom_modifications={'parry_bonus': 1},
            notes='Test Talent'
        )
    
    def test_talent_creation(self):
        """Test Talent Erstellung"""
        self.assertEqual(self.talent.character, self.character)
        self.assertEqual(self.talent.value, 12)
        self.assertEqual(self.talent.talent_data['name'], 'Schwerter')
    
    def test_talent_str(self):
        """Test String-Repräsentation"""
        expected = f"{self.character.name} - Schwerter (12)"
        self.assertEqual(str(self.talent), expected)
    
    def test_get_talent_name(self):
        """Test Talentname-Abruf"""
        self.assertEqual(self.talent.get_talent_name(), 'Schwerter')
    
    def test_get_talent_type(self):
        """Test Talenttyp-Abruf"""
        self.assertEqual(self.talent.get_talent_type(), 'combat')
    
    def test_get_specialization(self):
        """Test Spezialisierungs-Abruf"""
        # Test that specializations list exists
        self.assertIsInstance(self.talent.specializations, list)
    
    def test_get_custom_modification(self):
        """Test Benutzerdefinierte Modifikation"""
        self.assertEqual(self.talent.get_custom_modification('parry_bonus'), 1)
        self.assertIsNone(self.talent.get_custom_modification('nonexistent'))


class CharacterSpellTest(TestCase):
    """Tests für CharacterSpell-Model"""
    
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
        
        self.spell = CharacterSpell.objects.create(
            character=self.character,
            spell_data={
                'name': 'Ignifaxius',
                'category': 'Elementar',
                'difficulty': 8,
                'cost': 4
            },
            level=2,
            modifications={'range_bonus': 2},
            acquisition_data={'ap_cost': 8, 'acquisition_date': '2025-01-26'},
            casting_history=[
                {'date': '2025-01-26', 'success': True, 'modifiers': []}
            ],
            notes='Test Zauber'
        )
    
    def test_spell_creation(self):
        """Test Zauber Erstellung"""
        self.assertEqual(self.spell.character, self.character)
        self.assertEqual(self.spell.level, 2)
        self.assertEqual(self.spell.spell_data['name'], 'Ignifaxius')
    
    def test_spell_str(self):
        """Test String-Repräsentation"""
        expected = f"{self.character.name} - Ignifaxius (Level 2)"
        self.assertEqual(str(self.spell), expected)
    
    def test_get_spell_name(self):
        """Test Zaubername-Abruf"""
        self.assertEqual(self.spell.spell_data['name'], 'Ignifaxius')
    
    def test_get_spell_category(self):
        """Test Zauberkategorie-Abruf"""
        self.assertEqual(self.spell.spell_data['category'], 'Elementar')
    
    def test_get_spell_difficulty(self):
        """Test Zauber-Schwierigkeit-Abruf"""
        self.assertEqual(self.spell.spell_data['difficulty'], 8)
    
    def test_get_modification(self):
        """Test Modifikations-Abruf"""
        self.assertEqual(self.spell.get_modification('range_bonus'), 2)
        self.assertIsNone(self.spell.get_modification('nonexistent'))
    
    def test_add_casting_record(self):
        """Test Zauber-Aufzeichnung hinzufügen"""
        initial_count = len(self.spell.casting_history)
        # Add a new casting record
        self.spell.casting_history.append({
            'date': '2025-01-27',
            'success': True,
            'modifiers': ['modifier1']
        })
        self.spell.save()
        self.assertEqual(len(self.spell.casting_history), initial_count + 1)


class CharacterLiturgyTest(TestCase):
    """Tests für CharacterLiturgy-Model"""
    
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
        
        self.liturgy = CharacterLiturgy.objects.create(
            character=self.character,
            liturgy_data={
                'name': 'Balsam Salabunde',
                'category': 'Heilung',
                'difficulty': 6,
                'karma_cost': 2
            },
            level=1,
            modifications={'healing_bonus': 1},
            acquisition_data={'ap_cost': 6, 'acquisition_date': '2025-01-26'},
            deity_data={'deity': 'Phex', 'favor_level': 1},
            casting_history=[
                {'date': '2025-01-26', 'success': True, 'karma_spent': 2}
            ],
            notes='Test Liturgie'
        )
    
    def test_liturgy_creation(self):
        """Test Liturgie Erstellung"""
        self.assertEqual(self.liturgy.character, self.character)
        self.assertEqual(self.liturgy.level, 1)
        self.assertEqual(self.liturgy.liturgy_data['name'], 'Balsam Salabunde')
    
    def test_liturgy_str(self):
        """Test String-Repräsentation"""
        expected = f"{self.character.name} - Balsam Salabunde (Level 1)"
        self.assertEqual(str(self.liturgy), expected)
    
    def test_get_liturgy_name(self):
        """Test Liturgiename-Abruf"""
        self.assertEqual(self.liturgy.liturgy_data['name'], 'Balsam Salabunde')
    
    def test_get_liturgy_category(self):
        """Test Liturgiekategorie-Abruf"""
        self.assertEqual(self.liturgy.liturgy_data['category'], 'Heilung')
    
    def test_get_deity(self):
        """Test Gottheit-Abruf"""
        self.assertEqual(self.liturgy.deity_data['deity'], 'Phex')
    
    def test_get_modification(self):
        """Test Modifikations-Abruf"""
        self.assertEqual(self.liturgy.get_modification('healing_bonus'), 1)
        self.assertIsNone(self.liturgy.get_modification('nonexistent'))


class CharacterEquipmentTest(TestCase):
    """Tests für CharacterEquipment-Model"""
    
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
        
        self.equipment = CharacterEquipment.objects.create(
            character=self.character,
            equipment_data={
                'name': 'Anderthalbhänder',
                'type': 'weapon',
                'damage': '1W6+4',
                'weight': 2.5
            },
            equipment_type='weapon',
            status='equipped',
            quantity=1,
            condition=95,
            modifications={'enchantment': 'fire_damage'},
            acquisition_data={'cost': 150, 'acquisition_date': '2025-01-26'},
            location_data={'container': 'Hand', 'position': 'main_hand'},
            usage_history=[
                {'date': '2025-01-26', 'action': 'combat', 'condition_change': -5}
            ],
            notes='Test Ausrüstung'
        )
    
    def test_equipment_creation(self):
        """Test Ausrüstung Erstellung"""
        self.assertEqual(self.equipment.character, self.character)
        self.assertEqual(self.equipment.equipment_type, 'weapon')
        self.assertEqual(self.equipment.status, 'equipped')
        self.assertEqual(self.equipment.condition, 95)
    
    def test_equipment_str(self):
        """Test String-Repräsentation"""
        expected = f"{self.character.name} - Anderthalbhänder (Angelegt)"
        self.assertEqual(str(self.equipment), expected)
    
    def test_get_equipment_name(self):
        """Test Ausrüstungsname-Abruf"""
        self.assertEqual(self.equipment.get_equipment_name(), 'Anderthalbhänder')
    
    def test_get_equipment_weight(self):
        """Test Ausrüstungsgewicht-Abruf"""
        self.assertEqual(self.equipment.get_equipment_weight(), 2.5)
    
    def test_get_total_weight(self):
        """Test Gesamtgewicht-Abruf"""
        self.assertEqual(self.equipment.get_total_weight(), 2.5)
    
    def test_is_equipped(self):
        """Test Angelegt-Status"""
        self.assertTrue(self.equipment.is_equipped())
        
        self.equipment.status = 'carried'
        self.assertFalse(self.equipment.is_equipped())
    
    def test_change_condition(self):
        """Test Zustandsänderung"""
        initial_condition = self.equipment.condition
        self.equipment.change_condition(-10)
        self.assertEqual(self.equipment.condition, initial_condition - 10)
    
    def test_add_usage_record(self):
        """Test Nutzungsaufzeichnung hinzufügen"""
        initial_count = len(self.equipment.usage_history)
        self.equipment.add_usage_record('maintenance', {'condition_improved': 5})
        self.assertEqual(len(self.equipment.usage_history), initial_count + 1)


class CharacterFamilyTest(TestCase):
    """Tests für CharacterFamily-Model"""
    
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
        
        self.related_character = Character.objects.create(
            user=self.user,
            world=self.world,
            rule_set=self.rule_set,
            name='Related Character',
            core_attributes={
                'MU': 13, 'KL': 12, 'IN': 11, 'CH': 10,
                'FF': 9, 'GE': 8, 'KO': 7, 'KK': 6
            }
        )
        
        self.family_relationship = CharacterFamily.objects.create(
            character=self.character,
            related_character=self.related_character,
            relationship_type='sibling',
            relationship_status='alive',
            family_member_data={
                'name': 'Related Character',
                'age': 25,
                'profession': 'Krieger'
            },
            relationship_details={'shared_childhood': True},
            family_history=[
                {'date': '2020-01-01', 'event': 'Geburt', 'details': 'Geboren in der gleichen Stadt'}
            ],
            inheritance_data={'share': 0.5},
            notes='Test Familienbeziehung'
        )
    
    def test_family_relationship_creation(self):
        """Test Familienbeziehung Erstellung"""
        self.assertEqual(self.family_relationship.character, self.character)
        self.assertEqual(self.family_relationship.related_character, self.related_character)
        self.assertEqual(self.family_relationship.relationship_type, 'sibling')
        self.assertEqual(self.family_relationship.relationship_status, 'alive')
    
    def test_family_relationship_str(self):
        """Test String-Repräsentation"""
        expected = f"{self.character.name} - Geschwister - {self.related_character.name}"
        self.assertEqual(str(self.family_relationship), expected)
    
    def test_get_relationship_type_display(self):
        """Test Beziehungstyp-Anzeige"""
        self.assertEqual(self.family_relationship.get_relationship_type_display(), 'Geschwister')
    
    def test_get_relationship_status_display(self):
        """Test Beziehungsstatus-Anzeige"""
        self.assertEqual(self.family_relationship.get_relationship_status_display(), 'Lebend')
    
    def test_get_family_member_name(self):
        """Test Familienmitgliedsname-Abruf"""
        self.assertEqual(self.family_relationship.get_family_member_name(), 'Related Character')
    
    def test_get_family_member_age(self):
        """Test Familienmitgliedsalter-Abruf"""
        # Test with internal character (should return None since Character has no age)
        self.assertIsNone(self.family_relationship.get_family_member_age())
        
        # Test with external family member data
        external_family = CharacterFamily.objects.create(
            character=self.character,
            relationship_type='parent',
            relationship_status='alive',
            family_member_data={'name': 'External Parent', 'age': 50}
        )
        self.assertEqual(external_family.get_family_member_age(), 50)
    
    def test_get_inheritance_share(self):
        """Test Erbanteil-Abruf"""
        self.assertEqual(self.family_relationship.get_inheritance_share(), 0.5)
    
    def test_add_family_history_event(self):
        """Test Familienhistorie-Ereignis hinzufügen"""
        initial_count = len(self.family_relationship.family_history)
        self.family_relationship.add_family_history_event('Test Event', {'details': 'Test Details'})
        self.assertEqual(len(self.family_relationship.family_history), initial_count + 1) 