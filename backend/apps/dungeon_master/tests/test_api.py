"""
Test cases for Dungeon Master API endpoints.
"""
import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import DungeonMaster


class DungeonMasterAPITest(APITestCase):
    """
    Test cases for DungeonMaster API endpoints.
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
        self.dm = DungeonMaster.objects.create(
            user=self.user,
            game_system_setting={'system': 'dnd5e'},
            ui_settings={'theme': 'dark'},
            ai_settings={'model': 'gpt-4'}
        )
        
        # Test data for creating new DM
        self.create_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'game_system_setting': {'system': 'pathfinder'},
            'ui_settings': {'theme': 'light'},
            'ai_settings': {'model': 'gpt-3.5'}
        }
    
    def test_create_dungeon_master(self):
        """
        Test creating a new DungeonMaster via API.
        """
        url = reverse('dungeon_master:create')
        response = self.client.post(url, self.create_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that user was created
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.email, 'new@example.com')
        
        # Check that DM profile was created
        new_dm = DungeonMaster.objects.get(user=new_user)
        self.assertEqual(new_dm.game_system_setting['system'], 'pathfinder')
        self.assertIsNotNone(new_dm.entity_id)
    
    def test_create_dungeon_master_duplicate_username(self):
        """
        Test creating DM with duplicate username.
        """
        url = reverse('dungeon_master:create')
        self.create_data['username'] = 'testuser'  # Already exists
        
        response = self.client.post(url, self.create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
    
    def test_create_dungeon_master_duplicate_email(self):
        """
        Test creating DM with duplicate email.
        """
        url = reverse('dungeon_master:create')
        self.create_data['email'] = 'test@example.com'  # Already exists
        
        response = self.client.post(url, self.create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_get_dungeon_master_detail(self):
        """
        Test getting DungeonMaster detail.
        """
        url = reverse('dungeon_master:detail', kwargs={'entity_id': self.dm.entity_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['entity_id'], self.dm.entity_id)
        self.assertEqual(response.data['user']['username'], self.user.username)
        self.assertEqual(response.data['game_system_setting']['system'], 'dnd5e')
    
    def test_get_dungeon_master_not_found(self):
        """
        Test getting non-existent DungeonMaster.
        """
        url = reverse('dungeon_master:detail', kwargs={'entity_id': 'dm-nonexistent'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_list_dungeon_masters(self):
        """
        Test listing DungeonMasters.
        """
        # Create another DM
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        dm2 = DungeonMaster.objects.create(user=user2)
        
        url = reverse('dungeon_master:list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_update_dungeon_master_profile(self):
        """
        Test updating DungeonMaster profile.
        """
        url = reverse('dungeon_master:update_profile', kwargs={'entity_id': self.dm.entity_id})
        update_data = {
            'game_system_setting': {'system': 'pathfinder', 'edition': '2e'},
            'ui_settings': {'theme': 'light', 'sidebar': 'expanded'}
        }
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.dm.refresh_from_db()
        self.assertEqual(self.dm.game_system_setting['system'], 'pathfinder')
        self.assertEqual(self.dm.ui_settings['theme'], 'light')
    
    def test_update_user_info(self):
        """
        Test updating User information.
        """
        url = reverse('dungeon_master:update_user', kwargs={'entity_id': self.dm.entity_id})
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.email, 'updated@example.com')
    
    def test_delete_dungeon_master(self):
        """
        Test deleting DungeonMaster (soft delete).
        """
        url = reverse('dungeon_master:delete', kwargs={'entity_id': self.dm.entity_id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check soft delete
        self.dm.refresh_from_db()
        self.assertFalse(self.dm.is_active)
    
    def test_update_game_system_setting(self):
        """
        Test updating individual game system setting.
        """
        url = reverse('dungeon_master:update_game_setting', kwargs={'entity_id': self.dm.entity_id})
        update_data = {
            'key': 'edition',
            'value': '5e'
        }
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.dm.refresh_from_db()
        self.assertEqual(self.dm.game_system_setting['edition'], '5e')
    
    def test_update_ui_setting(self):
        """
        Test updating individual UI setting.
        """
        url = reverse('dungeon_master:update_ui_setting', kwargs={'entity_id': self.dm.entity_id})
        update_data = {
            'key': 'language',
            'value': 'de'
        }
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.dm.refresh_from_db()
        self.assertEqual(self.dm.ui_settings['language'], 'de')
    
    def test_update_ai_setting(self):
        """
        Test updating individual AI setting.
        """
        url = reverse('dungeon_master:update_ai_setting', kwargs={'entity_id': self.dm.entity_id})
        update_data = {
            'key': 'temperature',
            'value': 0.8
        }
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.dm.refresh_from_db()
        self.assertEqual(self.dm.ai_settings['temperature'], 0.8)
    
    def test_invalid_json_in_settings(self):
        """
        Test handling of invalid JSON in settings.
        """
        url = reverse('dungeon_master:update_profile', kwargs={'entity_id': self.dm.entity_id})
        update_data = {
            'game_system_setting': 'invalid json string'
        }
        
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_pagination(self):
        """
        Test pagination in list endpoint.
        """
        # Create multiple DMs
        for i in range(15):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123'
            )
            DungeonMaster.objects.create(user=user)
        
        url = reverse('dungeon_master:list')
        response = self.client.get(url + '?page_size=5')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNotNone(response.data['next']) 