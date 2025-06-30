"""
Test cases for Adventure models.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from apps.dungeon_master.models import DungeonMaster
from ..models import Adventure


class AdventureModelTest(TestCase):
    """
    Test cases for the Adventure model.
    """
    
    def setUp(self):
        """
        Set up test data.
        """
        self.user = User.objects.create_user(
            username='testdm',
            email='test@example.com',
            password='testpass123'
        )
        self.dm = DungeonMaster.objects.create(user=self.user)
        
        self.adventure_data = {
            'name': 'Test Adventure',
            'description': 'A test adventure for testing purposes',
            'game_system': 'D&D 5e',
            'player_count': 4
        }
    
    def test_adventure_creation(self):
        """
        Test creating an Adventure.
        """
        adventure = Adventure.objects.create(
            dungeon_master=self.dm,
            **self.adventure_data
        )
        
        self.assertEqual(adventure.dungeon_master, self.dm)
        self.assertEqual(adventure.name, 'Test Adventure')
        self.assertTrue(adventure.entity_id.startswith('adv-'))
        self.assertEqual(len(adventure.entity_id), 16)  # adv- + 12 digits
        self.assertEqual(adventure.status, 'planning')
        self.assertFalse(adventure.is_public)
        self.assertEqual(adventure.current_session, 0)
        self.assertEqual(adventure.total_sessions, 0)
        self.assertIsNotNone(adventure.created_at)
        self.assertIsNotNone(adventure.updated_at)
    
    def test_entity_id_generation(self):
        """
        Test that entity_id is automatically generated and unique.
        """
        adventure1 = Adventure.objects.create(
            dungeon_master=self.dm,
            name='Adventure 1',
            game_system='D&D 5e'
        )
        
        # Create another DM and adventure
        user2 = User.objects.create_user(
            username='testdm2',
            email='test2@example.com',
            password='testpass123'
        )
        dm2 = DungeonMaster.objects.create(user=user2)
        adventure2 = Adventure.objects.create(
            dungeon_master=dm2,
            name='Adventure 2',
            game_system='Pathfinder'
        )
        
        self.assertNotEqual(adventure1.entity_id, adventure2.entity_id)
        self.assertTrue(adventure1.entity_id.startswith('adv-'))
        self.assertTrue(adventure2.entity_id.startswith('adv-'))
    
    def test_adventure_limit_per_dm(self):
        """
        Test that a DM can only have 2 adventures maximum.
        """
        # Create first adventure
        Adventure.objects.create(
            dungeon_master=self.dm,
            name='Adventure 1',
            game_system='D&D 5e'
        )
        
        # Create second adventure
        Adventure.objects.create(
            dungeon_master=self.dm,
            name='Adventure 2',
            game_system='Pathfinder'
        )
        
        # Try to create third adventure - should fail
        with self.assertRaises(ValueError):
            Adventure.objects.create(
                dungeon_master=self.dm,
                name='Adventure 3',
                game_system='Call of Cthulhu'
            )
    
    def test_string_representation(self):
        """
        Test the string representation of Adventure.
        """
        adventure = Adventure.objects.create(
            dungeon_master=self.dm,
            **self.adventure_data
        )
        expected = f"{self.adventure_data['name']} ({adventure.entity_id})"
        self.assertEqual(str(adventure), expected)
    
    def test_dm_username_property(self):
        """
        Test the dm_username property.
        """
        adventure = Adventure.objects.create(
            dungeon_master=self.dm,
            **self.adventure_data
        )
        self.assertEqual(adventure.dm_username, self.user.username)
    
    def test_is_active_property(self):
        """
        Test the is_active property.
        """
        adventure = Adventure.objects.create(
            dungeon_master=self.dm,
            **self.adventure_data
        )
        
        # Initially planning, not active
        self.assertFalse(adventure.is_active)
        
        # Set to active
        adventure.status = 'active'
        adventure.save()
        self.assertTrue(adventure.is_active)
    
    def test_session_count_property(self):
        """
        Test the session_count property.
        """
        adventure = Adventure.objects.create(
            dungeon_master=self.dm,
            **self.adventure_data,
            session_notes=[
                {'session': 1, 'notes': 'First session'},
                {'session': 2, 'notes': 'Second session'}
            ]
        )
        
        self.assertEqual(adventure.session_count, 2)
    
    def test_json_field_operations(self):
        """
        Test JSON field operations.
        """
        adventure = Adventure.objects.create(
            dungeon_master=self.dm,
            name='Test Adventure',
            game_system='D&D 5e',
            adventure_settings={'difficulty': 'normal', 'house_rules': ['flanking']},
            world_building={'locations': ['Tavern', 'Forest'], 'npcs': ['Bartender']},
            session_notes=[{'session': 1, 'summary': 'Started in tavern'}]
        )
        
        # Test retrieval
        self.assertEqual(adventure.adventure_settings['difficulty'], 'normal')
        self.assertEqual(len(adventure.world_building['locations']), 2)
        self.assertEqual(len(adventure.session_notes), 1)
        
        # Test modification
        adventure.adventure_settings['new_rule'] = 'custom'
        adventure.save()
        
        # Refresh from database
        adventure.refresh_from_db()
        self.assertEqual(adventure.adventure_settings['new_rule'], 'custom')
    
    def test_get_adventure_setting(self):
        """
        Test get_adventure_setting method.
        """
        adventure = Adventure.objects.create(
            dungeon_master=self.dm,
            **self.adventure_data,
            adventure_settings={'difficulty': 'hard', 'xp_multiplier': 1.5}
        )
        
        self.assertEqual(adventure.get_adventure_setting('difficulty'), 'hard')
        self.assertEqual(adventure.get_adventure_setting('xp_multiplier'), 1.5)
        self.assertIsNone(adventure.get_adventure_setting('nonexistent'))
        self.assertEqual(adventure.get_adventure_setting('nonexistent', 'default'), 'default')
    
    def test_set_adventure_setting(self):
        """
        Test set_adventure_setting method.
        """
        adventure = Adventure.objects.create(
            dungeon_master=self.dm,
            **self.adventure_data
        )
        
        adventure.set_adventure_setting('difficulty', 'extreme')
        adventure.refresh_from_db()
        
        self.assertEqual(adventure.adventure_settings['difficulty'], 'extreme')
    
    def test_add_session_note(self):
        """
        Test add_session_note method.
        """
        adventure = Adventure.objects.create(
            dungeon_master=self.dm,
            **self.adventure_data
        )
        
        note_data = {
            'summary': 'Party defeated the goblins',
            'xp_gained': 200,
            'date': '2023-12-01'
        }
        
        adventure.add_session_note(note_data)
        adventure.refresh_from_db()
        
        self.assertEqual(len(adventure.session_notes), 1)
        self.assertEqual(adventure.session_notes[0]['session_number'], 1)
        self.assertEqual(adventure.session_notes[0]['summary'], 'Party defeated the goblins')
        self.assertEqual(adventure.total_sessions, 1)
    
    def test_update_status(self):
        """
        Test update_status method.
        """
        adventure = Adventure.objects.create(
            dungeon_master=self.dm,
            **self.adventure_data
        )
        
        # Start the adventure
        adventure.update_status('active')
        self.assertEqual(adventure.status, 'active')
        self.assertIsNotNone(adventure.started_at)
        
        # Complete the adventure
        adventure.update_status('completed')
        self.assertEqual(adventure.status, 'completed')
        self.assertIsNotNone(adventure.completed_at)
    
    def test_get_character_count(self):
        """
        Test get_character_count method.
        """
        adventure = Adventure.objects.create(
            dungeon_master=self.dm,
            **self.adventure_data,
            character_sheets=[
                {'name': 'Aragorn', 'class': 'Ranger'},
                {'name': 'Legolas', 'class': 'Fighter'},
                {'name': 'Gimli', 'class': 'Fighter'}
            ]
        )
        
        self.assertEqual(adventure.get_character_count(), 3)
    
    def test_player_count_validation(self):
        """
        Test player count validation constraints.
        """
        # Valid player count
        adventure = Adventure.objects.create(
            dungeon_master=self.dm,
            name='Test Adventure',
            game_system='D&D 5e',
            player_count=5
        )
        self.assertEqual(adventure.player_count, 5)
        
        # Test boundary values
        adventure.player_count = 0
        adventure.save()  # Should not raise
        
        adventure.player_count = 10
        adventure.save()  # Should not raise
    
    def test_status_choices(self):
        """
        Test that status field accepts valid choices.
        """
        valid_statuses = ['planning', 'active', 'paused', 'completed', 'archived']
        
        adventure = Adventure.objects.create(
            dungeon_master=self.dm,
            **self.adventure_data
        )
        
        for status in valid_statuses:
            adventure.status = status
            adventure.save()  # Should not raise
            self.assertEqual(adventure.status, status)
    
    def test_model_meta_options(self):
        """
        Test model meta options.
        """
        adventure1 = Adventure.objects.create(
            dungeon_master=self.dm,
            name='Adventure 1',
            game_system='D&D 5e'
        )
        
        # Create second adventure slightly later
        adventure2 = Adventure.objects.create(
            dungeon_master=self.dm,
            name='Adventure 2',
            game_system='Pathfinder'
        )
        
        # Test ordering (most recent first)
        adventures = list(Adventure.objects.all())
        self.assertEqual(adventures[0], adventure2)
        self.assertEqual(adventures[1], adventure1)
    
    def test_cascade_deletion(self):
        """
        Test that Adventure is deleted when DungeonMaster is deleted.
        """
        adventure = Adventure.objects.create(
            dungeon_master=self.dm,
            **self.adventure_data
        )
        adventure_id = adventure.id
        
        # Delete dungeon master
        self.dm.delete()
        
        # Adventure should be deleted too
        with self.assertRaises(Adventure.DoesNotExist):
            Adventure.objects.get(id=adventure_id) 