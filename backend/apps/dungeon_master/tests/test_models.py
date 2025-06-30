"""
Test cases for Dungeon Master models.
"""
import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from ..models import DungeonMaster


class DungeonMasterModelTest(TestCase):
    """
    Test cases for the DungeonMaster model.
    """
    
    def setUp(self):
        """
        Set up test data.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_dungeon_master_creation(self):
        """
        Test creating a DungeonMaster instance.
        """
        dm = DungeonMaster.objects.create(user=self.user)
        
        self.assertIsNotNone(dm.entity_id)
        self.assertTrue(dm.entity_id.startswith('dm-'))
        self.assertEqual(dm.user, self.user)
        self.assertTrue(dm.is_active)
        self.assertEqual(dm.game_system_setting, {})
        self.assertEqual(dm.ui_settings, {})
        self.assertEqual(dm.ai_settings, {})
    
    def test_dungeon_master_str_representation(self):
        """
        Test string representation of DungeonMaster.
        """
        dm = DungeonMaster.objects.create(user=self.user)
        expected = f"{self.user.username} ({dm.entity_id})"
        self.assertEqual(str(dm), expected)
    
    def test_full_name_property(self):
        """
        Test the full_name property.
        """
        self.user.first_name = 'John'
        self.user.last_name = 'Doe'
        self.user.save()
        
        dm = DungeonMaster.objects.create(user=self.user)
        self.assertEqual(dm.full_name, 'John Doe')
        
        # Test with empty first/last name
        self.user.first_name = ''
        self.user.last_name = ''
        self.user.save()
        self.assertEqual(dm.full_name, self.user.username)
    
    def test_email_property(self):
        """
        Test the email property.
        """
        dm = DungeonMaster.objects.create(user=self.user)
        self.assertEqual(dm.email, self.user.email)
    
    def test_setting_methods(self):
        """
        Test setting getter and setter methods.
        """
        dm = DungeonMaster.objects.create(user=self.user)
        
        # Test game system settings
        dm.set_game_system_setting('theme', 'fantasy')
        self.assertEqual(dm.get_game_system_setting('theme'), 'fantasy')
        self.assertIsNone(dm.get_game_system_setting('nonexistent'))
        self.assertEqual(dm.get_game_system_setting('nonexistent', 'default'), 'default')
        
        # Test UI settings
        dm.set_ui_setting('dark_mode', True)
        self.assertTrue(dm.get_ui_setting('dark_mode'))
        
        # Test AI settings
        dm.set_ai_setting('model', 'gpt-4')
        self.assertEqual(dm.get_ai_setting('model'), 'gpt-4')
    
    def test_entity_id_generation(self):
        """
        Test that entity_id is automatically generated.
        """
        dm1 = DungeonMaster.objects.create(user=self.user)
        
        # Create another user and DM to test uniqueness
        user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com',
            password='testpass123'
        )
        dm2 = DungeonMaster.objects.create(user=user2)
        
        self.assertNotEqual(dm1.entity_id, dm2.entity_id)
        self.assertTrue(dm1.entity_id.startswith('dm-'))
        self.assertTrue(dm2.entity_id.startswith('dm-'))
    
    def test_one_to_one_relationship(self):
        """
        Test that User can only have one DungeonMaster profile.
        """
        DungeonMaster.objects.create(user=self.user)
        
        # Try to create another DM for the same user
        with self.assertRaises(IntegrityError):
            DungeonMaster.objects.create(user=self.user)
    
    def test_json_field_operations(self):
        """
        Test JSON field operations.
        """
        dm = DungeonMaster.objects.create(
            user=self.user,
            game_system_setting={'system': 'dnd5e', 'rules': ['basic']},
            ui_settings={'theme': 'dark', 'language': 'en'},
            ai_settings={'model': 'gpt-4', 'temperature': 0.7}
        )
        
        # Test retrieval
        self.assertEqual(dm.game_system_setting['system'], 'dnd5e')
        self.assertEqual(dm.ui_settings['theme'], 'dark')
        self.assertEqual(dm.ai_settings['model'], 'gpt-4')
        
        # Test modification
        dm.game_system_setting['new_rule'] = 'custom'
        dm.save()
        
        # Refresh from database
        dm.refresh_from_db()
        self.assertEqual(dm.game_system_setting['new_rule'], 'custom')
    
    def test_get_game_system_setting(self):
        """
        Test get_game_system_setting method.
        """
        dm = DungeonMaster.objects.create(
            user=self.user,
            game_system_setting={'system': 'dnd5e', 'level': 10}
        )
        
        self.assertEqual(dm.get_game_system_setting('system'), 'dnd5e')
        self.assertEqual(dm.get_game_system_setting('level'), 10)
        self.assertIsNone(dm.get_game_system_setting('nonexistent'))
        self.assertEqual(dm.get_game_system_setting('nonexistent', 'default'), 'default')
    
    def test_set_game_system_setting(self):
        """
        Test set_game_system_setting method.
        """
        dm = DungeonMaster.objects.create(user=self.user)
        
        dm.set_game_system_setting('system', 'pathfinder')
        dm.refresh_from_db()
        
        self.assertEqual(dm.game_system_setting['system'], 'pathfinder')
    
    def test_get_ui_setting(self):
        """
        Test get_ui_setting method.
        """
        dm = DungeonMaster.objects.create(
            user=self.user,
            ui_settings={'theme': 'light', 'sidebar': 'collapsed'}
        )
        
        self.assertEqual(dm.get_ui_setting('theme'), 'light')
        self.assertEqual(dm.get_ui_setting('sidebar'), 'collapsed')
        self.assertIsNone(dm.get_ui_setting('nonexistent'))
        self.assertEqual(dm.get_ui_setting('nonexistent', 'default'), 'default')
    
    def test_set_ui_setting(self):
        """
        Test set_ui_setting method.
        """
        dm = DungeonMaster.objects.create(user=self.user)
        
        dm.set_ui_setting('theme', 'dark')
        dm.refresh_from_db()
        
        self.assertEqual(dm.ui_settings['theme'], 'dark')
    
    def test_get_ai_setting(self):
        """
        Test get_ai_setting method.
        """
        dm = DungeonMaster.objects.create(
            user=self.user,
            ai_settings={'model': 'gpt-4', 'max_tokens': 2048}
        )
        
        self.assertEqual(dm.get_ai_setting('model'), 'gpt-4')
        self.assertEqual(dm.get_ai_setting('max_tokens'), 2048)
        self.assertIsNone(dm.get_ai_setting('nonexistent'))
        self.assertEqual(dm.get_ai_setting('nonexistent', 'default'), 'default')
    
    def test_set_ai_setting(self):
        """
        Test set_ai_setting method.
        """
        dm = DungeonMaster.objects.create(user=self.user)
        
        dm.set_ai_setting('temperature', 0.8)
        dm.refresh_from_db()
        
        self.assertEqual(dm.ai_settings['temperature'], 0.8)
    
    def test_model_meta_options(self):
        """
        Test model meta options.
        """
        dm = DungeonMaster.objects.create(user=self.user)
        
        # Test ordering
        user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com',
            password='testpass123'
        )
        dm2 = DungeonMaster.objects.create(user=user2)
        
        dms = list(DungeonMaster.objects.all())
        self.assertEqual(dms[0], dm2)  # More recent first
        self.assertEqual(dms[1], dm)
    
    def test_cascade_deletion(self):
        """
        Test that DungeonMaster is deleted when User is deleted.
        """
        dm = DungeonMaster.objects.create(user=self.user)
        dm_id = dm.id
        
        # Delete user
        self.user.delete()
        
        # DungeonMaster should be deleted too
        with self.assertRaises(DungeonMaster.DoesNotExist):
            DungeonMaster.objects.get(id=dm_id) 