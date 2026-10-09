"""
API Functionality Tests
Tests für die wichtigsten API-Funktionen zur Frontend-Integration
"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.characters.models import Character, RuleSet
from apps.world.models import World
from apps.permissions.models import Permission

User = get_user_model()


class CharacterAPIFunctionalityTest(APITestCase):
    """Tests für die wichtigsten Character-API-Funktionen"""
    
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='adminpass123'
        )
        
        # Create world
        self.world = World.objects.create(
            name='Test World',
            description='Test World Description',
            created_by=self.user
        )
        
        # Create rule set
        self.rule_set = RuleSet.objects.create(
            name='dsa_4_1',
            display_name='DSA 4.1',
            version='4.1',
            attribute_schema={},
            default_values={},
            is_active=True
        )
        
        # Grant admin permission
        Permission.grant_permission(
            user=self.admin_user,
            resource=self.world,
            permission_type='admin'
        )
    
    def test_character_crud_workflow(self):
        """Test: Complete Character CRUD Workflow"""
        self.client.force_authenticate(user=self.user)
        
        # 1. Create Character
        create_url = reverse('characters:character-list')
        create_data = {
            'name': 'Test Hero',
            'world': self.world.id,
            'rule_set': self.rule_set.id,
            'status': 'draft',
            'core_attributes': {
                'MU': 14, 'KL': 13, 'IN': 12, 'CH': 11,
                'FF': 10, 'GE': 9, 'KO': 8, 'KK': 8
            }
        }
        
        response = self.client.post(create_url, create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        character_id = response.data['id']
        
        # 2. Read Character
        detail_url = reverse('characters:character-detail', kwargs={'pk': character_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Hero')
        
        # 3. Update Character
        update_data = {
            'name': 'Updated Hero',
            'status': 'active'
        }
        response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Hero')
        
        # 4. List Characters
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)
        
        # 5. Delete Character
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify deletion
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_admin_permissions(self):
        """Test: Admin kann alle Charaktere verwalten"""
        # Create character as regular user
        self.client.force_authenticate(user=self.user)
        
        create_url = reverse('characters:character-list')
        create_data = {
            'name': 'User Character',
            'world': self.world.id,
            'rule_set': self.rule_set.id,
            'status': 'active',
            'core_attributes': {
                'MU': 12, 'KL': 12, 'IN': 12, 'CH': 12,
                'FF': 12, 'GE': 12, 'KO': 12, 'KK': 12
            }
        }
        
        response = self.client.post(create_url, create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        character_id = response.data['id']
        
        # Switch to admin user
        self.client.force_authenticate(user=self.admin_user)
        
        # Admin can view character
        detail_url = reverse('characters:character-detail', kwargs={'pk': character_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Admin can update character
        update_data = {'name': 'Admin Updated Character'}
        response = self.client.patch(detail_url, update_data, format='json')
        
                
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Admin can see all characters in world
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            self.assertGreaterEqual(len(response.data['results']), 1)
        else:
            self.assertGreaterEqual(len(response.data), 1)
    
    def test_character_validation(self):
        """Test: Character-Validierung funktioniert"""
        self.client.force_authenticate(user=self.user)
        
        create_url = reverse('characters:character-list')
        
        # Test: Fehlende required fields
        invalid_data = {
            'name': '',  # Empty name
            'world': self.world.id,
            'rule_set': self.rule_set.id
        }
        
        response = self.client.post(create_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test: Invalid attributes (unter Minimum)
        invalid_attributes_data = {
            'name': 'Test Character',
            'world': self.world.id,
            'rule_set': self.rule_set.id,
            'core_attributes': {
                'MU': 7,  # Unter Minimum von 8
                'KL': 8, 'IN': 8, 'CH': 8,
                'FF': 8, 'GE': 8, 'KO': 8, 'KK': 8
            }
        }
        
        response = self.client.post(create_url, invalid_attributes_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
    
    def test_character_filtering_and_search(self):
        """Test: Character-Filterung und Suche"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create test characters
        characters_data = [
            {
                'name': 'Fighter Character',
                'status': 'active',
                                 'core_attributes': {
                     'MU': 14, 'KL': 10, 'IN': 10, 'CH': 12,
                     'FF': 8, 'GE': 12, 'KO': 14, 'KK': 14
                 }
            },
            {
                'name': 'Mage Character',
                'status': 'draft',
                                 'core_attributes': {
                     'MU': 12, 'KL': 14, 'IN': 14, 'CH': 10,
                     'FF': 10, 'GE': 8, 'KO': 8, 'KK': 8
                 }
            }
        ]
        
        create_url = reverse('characters:character-list')
        
        for char_data in characters_data:
            char_data.update({
                'world': self.world.id,
                'rule_set': self.rule_set.id
            })
            response = self.client.post(create_url, char_data, format='json')
            

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test: Filter by status
        response = self.client.get(create_url, {'status': 'active'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test: Search by name
        response = self.client.get(create_url, {'search': 'Fighter'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test: Filter by world
        response = self.client.get(create_url, {'world': self.world.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_character_serialization(self):
        """Test: Character-Serialisierung für Frontend"""
        self.client.force_authenticate(user=self.user)
        
        # Create character
        create_url = reverse('characters:character-list')
        create_data = {
            'name': 'Serialization Test',
            'world': self.world.id,
            'rule_set': self.rule_set.id,
            'status': 'active',
            'core_attributes': {
                'MU': 14, 'KL': 13, 'IN': 12, 'CH': 11,
                'FF': 10, 'GE': 9, 'KO': 8, 'KK': 8
            }
        }
        
        response = self.client.post(create_url, create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify response structure for frontend
        required_fields = ['id', 'name', 'status', 'world_name', 'created_at']
        for field in required_fields:
            self.assertIn(field, response.data)
        
        # Get detailed view
        character_id = response.data['id']
        detail_url = reverse('characters:character-detail', kwargs={'pk': character_id})
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        detailed_fields = ['id', 'name', 'status', 'core_attributes', 'world_name', 'created_at', 'updated_at']
        for field in detailed_fields:
            self.assertIn(field, response.data)
    
    def test_authentication_required(self):
        """Test: Authentication ist erforderlich"""
        # Test without authentication
        create_url = reverse('characters:character-list')
        
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.post(create_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 