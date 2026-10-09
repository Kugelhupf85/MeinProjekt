"""
Region CRUD Tests - Comprehensive testing for Region operations
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.world.models import World, Region
from apps.permissions.models.permission import Permission

User = get_user_model()


class RegionCRUDTestCase(TestCase):
    """Test case for Region CRUD operations with permission integration."""
    
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
            description='A test world for region operations',
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
        
        # Create test region
        self.region = Region.objects.create(
            world=self.world,
            name='Test Region',
            description='A test region for CRUD operations',
            general_mood='Peaceful and prosperous',
            terrain_type='Plains',
            size_description='Medium-sized region'
        )
    
    def test_region_list_with_permissions(self):
        """Test that users can only see regions in worlds they have access to."""
        # User1 should see the region (admin permission on world)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Region')
        
        # User2 should see the region (view permission on world)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Unauthorized user should not see regions
        unauthorized_user = User.objects.create_user(
            email='unauthorized@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=unauthorized_user)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_region_create(self):
        """Test region creation with proper permissions."""
        self.client.force_authenticate(user=self.user1)
        
        region_data = {
            'name': 'New Test Region',
            'description': 'A newly created test region',
            'general_mood': 'Wild and untamed',
            'terrain_type': 'Forest',
            'size_description': 'Large forest region',
            'currencies': [
                {
                    'name': 'Forest Coin',
                    'exchange_rate': 1.0,
                    'is_primary': True
                }
            ],
            'important_personalities': [
                {
                    'name': 'Forest Guardian',
                    'role': 'Protector',
                    'importance': 8,
                    'description': 'Guardian of the forest'
                }
            ],
            'government_type': {
                'type': 'Tribal Council',
                'description': 'Council of tribal leaders'
            },
            'major_settlements': [
                {
                    'name': 'Forest Village',
                    'type': 'village',
                    'population': 500
                }
            ]
        }
        
        response = self.client.post(f'/api/world/worlds/{self.world.id}/regions/create/', region_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that region was created
        region = Region.objects.get(name='New Test Region')
        self.assertEqual(region.world, self.world)
        self.assertEqual(region.terrain_type, 'Forest')
        self.assertEqual(len(region.currencies), 1)
        self.assertEqual(region.currencies[0]['name'], 'Forest Coin')
        self.assertEqual(len(region.important_personalities), 1)
        self.assertEqual(region.important_personalities[0]['name'], 'Forest Guardian')
        
        # User2 should not be able to create regions (only view permission)
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/world/worlds/{self.world.id}/regions/create/', region_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_region_detail_get(self):
        """Test getting region details with proper permissions."""
        # User1 should be able to get details (admin permission on world)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Region')
        self.assertEqual(response.data['world_name'], 'Test World')
        
        # User2 should be able to get details (view permission on world)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Unauthorized user should not be able to get details
        unauthorized_user = User.objects.create_user(
            email='unauthorized@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=unauthorized_user)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_region_detail_update(self):
        """Test updating region details with proper permissions."""
        self.client.force_authenticate(user=self.user1)
        
        update_data = {
            'name': 'Updated Test Region',
            'description': 'Updated description',
            'general_mood': 'Updated mood',
            'terrain_type': 'Mountains'
        }
        
        response = self.client.put(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that region was updated
        self.region.refresh_from_db()
        self.assertEqual(self.region.name, 'Updated Test Region')
        self.assertEqual(self.region.terrain_type, 'Mountains')
        
        # User2 should not be able to update (only view permission on world)
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_region_detail_delete(self):
        """Test deleting region with proper permissions."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.delete(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check that region is soft deleted
        self.region.refresh_from_db()
        self.assertFalse(self.region.is_active)
        
        # User2 should not be able to delete (only view permission on world)
        region2 = Region.objects.create(
            world=self.world,
            name='Test Region 2',
            description='Another test region',
            general_mood='Test mood',
            terrain_type='Desert'
        )
        
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/api/world/worlds/{self.world.id}/regions/{region2.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_region_statistics(self):
        """Test region statistics endpoint."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stats = response.data
        self.assertEqual(stats['region_name'], 'Test Region')
        self.assertEqual(stats['location_count'], 0)  # No locations yet
        self.assertEqual(stats['major_settlements_count'], 0)
        self.assertEqual(stats['important_personalities_count'], 0)
    
    def test_region_search(self):
        """Test region search functionality."""
        self.client.force_authenticate(user=self.user1)
        
        # Search by name
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/search/?q=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Region')
        
        # Search with no results
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/search/?q=Nonexistent')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
        # Search without query parameter
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/search/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_region_validation(self):
        """Test region data validation."""
        self.client.force_authenticate(user=self.user1)
        
        # Test invalid data
        invalid_data = {
            'name': '',  # Empty name
            'description': 'A' * 3001,  # Too long description
        }
        
        response = self.client.post(f'/api/world/worlds/{self.world.id}/regions/create/', invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('description', response.data)
    
    def test_region_unique_constraints(self):
        """Test region name uniqueness within world."""
        self.client.force_authenticate(user=self.user1)
        
        # Try to create region with same name
        region_data = {
            'name': 'Test Region',  # Same name as existing region
            'description': 'Another test region',
            'general_mood': 'Test mood',
            'terrain_type': 'Desert'
        }
        
        response = self.client.post(f'/api/world/worlds/{self.world.id}/regions/create/', region_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_region_json_fields(self):
        """Test that JSON fields are properly handled."""
        self.client.force_authenticate(user=self.user1)
        
        region_data = {
            'name': 'JSON Test Region',
            'description': 'Testing JSON fields in regions',
            'general_mood': 'Complex',
            'terrain_type': 'Mixed',
            'size_description': 'Large mixed terrain region',
            'currencies': [
                {
                    'name': 'Gold Crown',
                    'exchange_rate': 1.0,
                    'is_primary': True
                },
                {
                    'name': 'Silver Mark',
                    'exchange_rate': 0.1,
                    'is_primary': False
                }
            ],
            'important_personalities': [
                {
                    'name': 'King Arthur',
                    'role': 'Monarch',
                    'importance': 10,
                    'description': 'The legendary king'
                },
                {
                    'name': 'Merlin',
                    'role': 'Wizard',
                    'importance': 9,
                    'description': 'The wise wizard'
                }
            ],
            'government_type': {
                'type': 'Monarchy',
                'description': 'Ruled by a king',
                'succession': 'Hereditary'
            },
            'cultural_traits': [
                'Honor-bound',
                'Chivalrous',
                'Magic-friendly'
            ],
            'major_settlements': [
                {
                    'name': 'Camelot',
                    'type': 'city',
                    'population': 10000,
                    'description': 'The capital city'
                }
            ],
            'natural_resources': [
                'Gold mines',
                'Fertile farmland',
                'Forest timber'
            ],
            'trade_specialties': [
                'Fine weapons',
                'Magical artifacts',
                'Agricultural products'
            ],
            'threats_dangers': [
                {
                    'name': 'Dragon',
                    'type': 'monster',
                    'danger_level': 'high',
                    'location': 'Mountain lair'
                }
            ],
            'climate_weather': {
                'type': 'Temperate',
                'seasons': ['Spring', 'Summer', 'Autumn', 'Winter'],
                'rainfall': 'Moderate'
            },
            'laws_customs': [
                'Honor duels are legal',
                'Magic requires license',
                'Knights have special privileges'
            ],
            'festivals_events': [
                {
                    'name': 'Tournament Season',
                    'frequency': 'annual',
                    'description': 'Knightly tournaments'
                }
            ],
            'military_forces': [
                {
                    'name': 'Royal Guard',
                    'type': 'professional',
                    'size': 1000,
                    'description': 'Elite royal protection'
                }
            ]
        }
        
        response = self.client.post(f'/api/world/worlds/{self.world.id}/regions/create/', region_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that JSON fields were saved correctly
        region = Region.objects.get(name='JSON Test Region')
        self.assertEqual(len(region.currencies), 2)
        self.assertEqual(region.currencies[0]['name'], 'Gold Crown')
        self.assertEqual(len(region.important_personalities), 2)
        self.assertEqual(region.important_personalities[0]['name'], 'King Arthur')
        self.assertEqual(region.government_type['type'], 'Monarchy')
        self.assertEqual(len(region.cultural_traits), 3)
        self.assertEqual(len(region.major_settlements), 1)
        self.assertEqual(region.major_settlements[0]['name'], 'Camelot')
        self.assertEqual(len(region.natural_resources), 3)
        self.assertEqual(len(region.trade_specialties), 3)
        self.assertEqual(len(region.threats_dangers), 1)
        self.assertEqual(region.threats_dangers[0]['name'], 'Dragon')
        self.assertEqual(region.climate_weather['type'], 'Temperate')
        self.assertEqual(len(region.laws_customs), 3)
        self.assertEqual(len(region.festivals_events), 1)
        self.assertEqual(len(region.military_forces), 1) 