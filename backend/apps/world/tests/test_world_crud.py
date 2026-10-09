"""
World CRUD Tests - Comprehensive testing for World operations
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from apps.world.models import World, WorldAPIKeys, WorldParty, WorldPartyMembership
from apps.permissions.models.permission import Permission

User = get_user_model()


class WorldCRUDTestCase(TestCase):
    """Test case for World CRUD operations with permission integration."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123',
            first_name='User',
            last_name='One'
        )
        
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123',
            first_name='User',
            last_name='Two'
        )
        
        # Create test world
        self.world = World.objects.create(
            name='Test World',
            description='A test world for CRUD operations',
            general_mood='Mysterious and adventurous',
            created_by=self.user1
        )
        
        # Grant permissions
        Permission.grant_permission(
            user=self.user1,
            resource=self.world,
            permission_type='admin',
            granted_by=self.user1
        )
        
        Permission.grant_permission(
            user=self.user2,
            resource=self.world,
            permission_type='view',
            granted_by=self.user1
        )
    
    def test_world_list_with_permissions(self):
        """Test that users can only see worlds they have access to."""
        # User1 should see the world (admin permission)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/world/worlds/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test World')
        
        # User2 should see the world (view permission)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/api/world/worlds/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Unauthenticated user should not see any worlds
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/world/worlds/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_world_create(self):
        """Test world creation with automatic permission assignment."""
        self.client.force_authenticate(user=self.user1)
        
        world_data = {
            'name': 'New Test World',
            'description': 'A newly created test world',
            'general_mood': 'Epic and grand',
            'current_date': 'Year 1, Month 1, Day 1',
            'time_system': {
                'calendar': 'Test Calendar',
                'months': ['First Month', 'Second Month'],
                'days_per_month': 30
            },
            'measurement_units': {
                'distance': {'league': '5 km'},
                'weight': {'stone': '6.35 kg'},
                'currency': {'gold_crown': 1}
            }
        }
        
        response = self.client.post('/api/world/worlds/create/', world_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that world was created
        world = World.objects.get(name='New Test World')
        self.assertEqual(world.created_by, self.user1)
        self.assertEqual(world.time_system['calendar'], 'Test Calendar')
        
        # Check that API keys and party were automatically created
        self.assertTrue(hasattr(world, 'api_keys'))
        self.assertTrue(hasattr(world, 'party'))
        
        # Check that creator has admin permission
        self.assertTrue(Permission.has_permission(self.user1, world, 'admin'))
    
    def test_world_detail_get(self):
        """Test getting world details with proper permissions."""
        # User1 should be able to get details (admin permission)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test World')
        
        # User2 should be able to get details (view permission)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Unauthorized user should not be able to get details
        unauthorized_user = User.objects.create_user(
            email='unauthorized@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=unauthorized_user)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_world_detail_update(self):
        """Test updating world details with proper permissions."""
        self.client.force_authenticate(user=self.user1)
        
        update_data = {
            'name': 'Updated Test World',
            'description': 'Updated description',
            'general_mood': 'Updated mood'
        }
        
        response = self.client.put(f'/api/world/worlds/{self.world.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that world was updated
        self.world.refresh_from_db()
        self.assertEqual(self.world.name, 'Updated Test World')
        
        # User2 should not be able to update (only view permission)
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(f'/api/world/worlds/{self.world.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_world_detail_delete(self):
        """Test deleting world with proper permissions."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.delete(f'/api/world/worlds/{self.world.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check that world is soft deleted
        self.world.refresh_from_db()
        self.assertFalse(self.world.is_active)
        
        # User2 should not be able to delete (only view permission)
        world2 = World.objects.create(
            name='Test World 2',
            description='Another test world',
            general_mood='Test mood',
            created_by=self.user1
        )
        Permission.grant_permission(
            user=self.user2,
            resource=world2,
            permission_type='view',
            granted_by=self.user1
        )
        
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/api/world/worlds/{world2.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_world_api_keys_access(self):
        """Test API keys access with proper permissions."""
        # User1 should be able to access API keys (admin permission)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/api-keys/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # User2 should not be able to access API keys (only view permission)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/api-keys/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_world_party_access(self):
        """Test party access with proper permissions."""
        # Both users should be able to access party details (view permission)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/party/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/party/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_world_party_invite(self):
        """Test party invitation with proper permissions."""
        new_user = User.objects.create_user(
            email='newuser@test.com',
            password='testpass123'
        )
        
        # User1 should be able to invite (edit permission)
        self.client.force_authenticate(user=self.user1)
        invite_data = {
            'user_email': 'newuser@test.com',
            'role': 'player'
        }
        
        response = self.client.post(f'/api/world/worlds/{self.world.id}/party/invite/', invite_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that membership was created
        membership = WorldPartyMembership.objects.get(user=new_user, party=self.world.party)
        self.assertEqual(membership.role, 'player')
        self.assertEqual(membership.status, 'invited')
        
        # Check that user got view permission
        self.assertTrue(Permission.has_permission(new_user, self.world, 'view'))
        
        # User2 should not be able to invite (only view permission)
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/world/worlds/{self.world.id}/party/invite/', invite_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_world_validation(self):
        """Test world data validation."""
        self.client.force_authenticate(user=self.user1)
        
        # Test invalid data
        invalid_data = {
            'name': '',  # Empty name
            'description': 'A' * 5001,  # Too long description
        }
        
        response = self.client.post('/api/world/worlds/create/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('description', response.data)
    
    def test_world_unique_constraints(self):
        """Test world name uniqueness constraints."""
        self.client.force_authenticate(user=self.user1)
        
        # Try to create world with same name
        world_data = {
            'name': 'Test World',  # Same name as existing world
            'description': 'Another test world',
            'general_mood': 'Test mood',
            'current_date': 'Year 1, Month 1, Day 1'
        }
        
        response = self.client.post('/api/world/worlds/create/', world_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_world_json_fields(self):
        """Test that JSON fields are properly handled."""
        self.client.force_authenticate(user=self.user1)
        
        world_data = {
            'name': 'JSON Test World',
            'description': 'Testing JSON fields',
            'general_mood': 'Complex',
            'current_date': 'Year 1, Month 1, Day 1',
            'time_system': {
                'calendar': 'Complex Calendar',
                'months': ['Month1', 'Month2', 'Month3'],
                'days_per_month': 28,
                'hours_per_day': 24
            },
            'measurement_units': {
                'distance': {
                    'league': '5 km',
                    'mile': '1.6 km',
                    'foot': '30 cm'
                },
                'weight': {
                    'stone': '6.35 kg',
                    'pound': '0.45 kg'
                },
                'currency': {
                    'gold_crown': 1,
                    'silver_mark': 0.1,
                    'copper_penny': 0.01
                }
            },
            'religions': [
                {
                    'name': 'Test Religion',
                    'description': 'A test religion',
                    'deities': ['Test God'],
                    'influence': 'high'
                }
            ],
            'magic_system': {
                'type': 'arcane',
                'schools': ['evocation', 'abjuration'],
                'limitations': ['no necromancy']
            }
        }
        
        response = self.client.post('/api/world/worlds/create/', world_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that JSON fields were saved correctly
        world = World.objects.get(name='JSON Test World')
        self.assertEqual(world.time_system['calendar'], 'Complex Calendar')
        self.assertEqual(len(world.time_system['months']), 3)
        self.assertEqual(world.measurement_units['distance']['league'], '5 km')
        self.assertEqual(len(world.religions), 1)
        self.assertEqual(world.religions[0]['name'], 'Test Religion')
        self.assertEqual(world.magic_system['type'], 'arcane') 