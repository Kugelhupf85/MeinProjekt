"""
Tests for Dungeon Master user models.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from ...models import DungeonMaster


class DungeonMasterModelTest(TestCase):
    """
    Test cases for DungeonMaster model.
    """
    
    def setUp(self):
        """
        Set up test data.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.dungeon_master = DungeonMaster.objects.create(
            user=self.user,
            game_system_setting={'system': 'D&D 5e'},
            ui_settings={'theme': 'dark'},
            ai_settings={'enabled': True}
        )
    
    def test_entity_id_generation(self):
        """
        Test that entity_id is automatically generated.
        """
        # Create new DM without entity_id
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        dm = DungeonMaster.objects.create(user=user2)
        
        # Check entity_id was generated
        self.assertIsNotNone(dm.entity_id)
        self.assertTrue(dm.entity_id.startswith('dm-'))
        self.assertEqual(len(dm.entity_id), 15)  # 'dm-' + 12 digits
    
    def test_entity_id_uniqueness(self):
        """
        Test that entity_id is unique.
        """
        # Create another DM
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        dm2 = DungeonMaster.objects.create(user=user2)
        
        # Entity IDs should be different
        self.assertNotEqual(self.dungeon_master.entity_id, dm2.entity_id)
    
    def test_str_representation(self):
        """
        Test string representation of DungeonMaster.
        """
        expected = f"{self.user.username} ({self.dungeon_master.entity_id})"
        self.assertEqual(str(self.dungeon_master), expected)
    
    def test_full_name_property(self):
        """
        Test full_name property.
        """
        self.assertEqual(self.dungeon_master.full_name, "Test User")
        
        # Test with no first/last name
        user2 = User.objects.create_user(
            username='noname',
            email='noname@example.com',
            password='testpass123'
        )
        dm2 = DungeonMaster.objects.create(user=user2)
        self.assertEqual(dm2.full_name, "noname")
    
    def test_email_property(self):
        """
        Test email property.
        """
        self.assertEqual(self.dungeon_master.email, 'test@example.com')
    
    def test_game_system_setting_methods(self):
        """
        Test game system setting getter/setter methods.
        """
        # Test get
        self.assertEqual(
            self.dungeon_master.get_game_system_setting('system'),
            'D&D 5e'
        )
        self.assertIsNone(
            self.dungeon_master.get_game_system_setting('nonexistent')
        )
        self.assertEqual(
            self.dungeon_master.get_game_system_setting('nonexistent', 'default'),
            'default'
        )
        
        # Test set
        self.dungeon_master.set_game_system_setting('level', 20)
        self.assertEqual(
            self.dungeon_master.get_game_system_setting('level'),
            20
        )
    
    def test_ui_setting_methods(self):
        """
        Test UI setting getter/setter methods.
        """
        # Test get
        self.assertEqual(
            self.dungeon_master.get_ui_setting('theme'),
            'dark'
        )
        
        # Test set
        self.dungeon_master.set_ui_setting('language', 'en')
        self.assertEqual(
            self.dungeon_master.get_ui_setting('language'),
            'en'
        )
    
    def test_ai_setting_methods(self):
        """
        Test AI setting getter/setter methods.
        """
        # Test get
        self.assertTrue(
            self.dungeon_master.get_ai_setting('enabled')
        )
        
        # Test set
        self.dungeon_master.set_ai_setting('model', 'gpt-4')
        self.assertEqual(
            self.dungeon_master.get_ai_setting('model'),
            'gpt-4'
        )
    
    def test_one_to_one_relationship(self):
        """
        Test that each User can only have one DungeonMaster.
        """
        with self.assertRaises(IntegrityError):
            DungeonMaster.objects.create(user=self.user)
    
    def test_default_values(self):
        """
        Test default values for JSON fields.
        """
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        dm = DungeonMaster.objects.create(user=user2)
        
        self.assertEqual(dm.game_system_setting, {})
        self.assertEqual(dm.ui_settings, {})
        self.assertEqual(dm.ai_settings, {})
        self.assertTrue(dm.is_active)
    
    def test_meta_options(self):
        """
        Test model meta options.
        """
        self.assertEqual(DungeonMaster._meta.db_table, 'dm_user_dungeonmaster')
        self.assertEqual(DungeonMaster._meta.verbose_name, 'Dungeon Master')
        self.assertEqual(DungeonMaster._meta.verbose_name_plural, 'Dungeon Masters')
        self.assertEqual(DungeonMaster._meta.ordering, ['-created_at']) 