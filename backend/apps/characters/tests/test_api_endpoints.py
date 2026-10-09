"""
Character API Endpoint Tests
Tests für Character API-Endpoints
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from apps.characters.models import Character, RuleSet
from apps.world.models import World

User = get_user_model()


class CharacterAPIEndpointsTest(APITestCase):
    """Tests für Character API-Endpoints"""
    
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
            attribute_schema={},
            default_values={},
            is_active=True
        )
        
        # Create character
        self.character = Character.objects.create(
            user=self.user,
            world=self.world,
            rule_set=self.rule_set,
            name='Test Character',
            status='active',
            core_attributes={
                'MU': 14, 'KL': 13, 'IN': 12, 'CH': 11,
                'FF': 10, 'GE': 9, 'KO': 8, 'KK': 7
            }
        )
        
        # Setup API client
        self.client = APIClient()
    
    def test_character_list_endpoint(self):
        """Test: Character List Endpoint"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('characters:character-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if we have results in the response
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Character')
    
    def test_character_detail_endpoint(self):
        """Test: Character Detail Endpoint"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('characters:character-detail', kwargs={'pk': self.character.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Character')
        # Check if world_name is in the response (instead of world)
        self.assertIn('world_name', response.data)
    
    def test_character_create_endpoint(self):
        """Test: Character Create Endpoint"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('characters:character-list')
        data = {
            'name': 'New Character',
            'world': self.world.id,
            'rule_set': self.rule_set.id,
            'core_attributes': {
                'MU': 12, 'KL': 11, 'IN': 10, 'CH': 9,
                'FF': 8, 'GE': 8, 'KO': 8, 'KK': 8
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Character.objects.count(), 2)
        # Check if the new character was created
        new_character = Character.objects.filter(name='New Character').first()
        self.assertIsNotNone(new_character)
    
    def test_character_update_endpoint(self):
        """Test: Character Update Endpoint"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('characters:character-detail', kwargs={'pk': self.character.id})
        data = {
            'name': 'Updated Character',
            'world': self.world.id,
            'rule_set': self.rule_set.id,
            'status': 'active'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.character.refresh_from_db()
        self.assertEqual(self.character.name, 'Updated Character')
    
    def test_character_delete_endpoint(self):
        """Test: Character Delete Endpoint"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('characters:character-detail', kwargs={'pk': self.character.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Character.objects.count(), 0) 