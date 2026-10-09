"""
Location CRUD Tests - Comprehensive testing for Location operations
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.world.models import World, Region, Location
from apps.permissions.models.permission import Permission

User = get_user_model()


class LocationCRUDTestCase(TestCase):
    """Test case for Location CRUD operations with permission integration."""
    
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
            description='A test world for location operations',
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
            description='A test region for location operations',
            general_mood='Peaceful and prosperous',
            terrain_type='Plains',
            size_description='Medium-sized region'
        )
        
        # Create test location
        self.location = Location.objects.create(
            region=self.region,
            name='Test Location',
            location_type='city',
            description='A test city for CRUD operations',
            general_mood='Bustling and busy',
            size_scale='Large',
            accessibility='Well-connected by roads'
        )
    
    def test_location_list_with_permissions(self):
        """Test that users can only see locations in worlds they have access to."""
        # User1 should see the location (admin permission on world)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/locations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Location')
        
        # User2 should see the location (view permission on world)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/locations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test location list by region
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/locations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Unauthorized user should not see locations
        unauthorized_user = User.objects.create_user(
            email='unauthorized@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=unauthorized_user)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/locations/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_location_create(self):
        """Test location creation with proper permissions."""
        self.client.force_authenticate(user=self.user1)
        
        location_data = {
            'name': 'New Test Location',
            'location_type': 'tavern',
            'description': 'A newly created test tavern',
            'general_mood': 'Warm and welcoming',
            'size_scale': 'Medium',
            'accessibility': 'Easy to find on main street',
            'important_personalities': [
                {
                    'name': 'Innkeeper',
                    'role': 'Owner',
                    'importance': 7,
                    'description': 'Friendly innkeeper'
                }
            ],
            'services_available': [
                {
                    'type': 'accommodation',
                    'name': 'Room rental',
                    'price': '2 silver per night',
                    'available': True
                },
                {
                    'type': 'food',
                    'name': 'Hot meals',
                    'price': '5 copper',
                    'available': True
                }
            ],
            'notable_features': [
                {
                    'name': 'Ancient fireplace',
                    'description': 'Magical warmth',
                    'significance': 'Local legend'
                }
            ]
        }
        
        response = self.client.post(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/locations/create/', location_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that location was created
        location = Location.objects.get(name='New Test Location')
        self.assertEqual(location.region, self.region)
        self.assertEqual(location.location_type, 'tavern')
        self.assertEqual(len(location.important_personalities), 1)
        self.assertEqual(location.important_personalities[0]['name'], 'Innkeeper')
        self.assertEqual(len(location.services_available), 2)
        self.assertEqual(location.services_available[0]['type'], 'accommodation')
        
        # User2 should not be able to create locations (only view permission on world)
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/locations/create/', location_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_location_detail_get(self):
        """Test getting location details with proper permissions."""
        # User1 should be able to get details (admin permission on world)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/locations/{self.location.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Location')
        self.assertEqual(response.data['region_name'], 'Test Region')
        self.assertEqual(response.data['world_name'], 'Test World')
        
        # User2 should be able to get details (view permission on world)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/locations/{self.location.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Unauthorized user should not be able to get details
        unauthorized_user = User.objects.create_user(
            email='unauthorized@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=unauthorized_user)
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/locations/{self.location.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_location_detail_update(self):
        """Test updating location details with proper permissions."""
        self.client.force_authenticate(user=self.user1)
        
        update_data = {
            'name': 'Updated Test Location',
            'description': 'Updated description',
            'general_mood': 'Updated mood',
            'location_type': 'castle'
        }
        
        response = self.client.put(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/locations/{self.location.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that location was updated
        self.location.refresh_from_db()
        self.assertEqual(self.location.name, 'Updated Test Location')
        self.assertEqual(self.location.location_type, 'castle')
        
        # User2 should not be able to update (only view permission on world)
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/locations/{self.location.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_location_detail_delete(self):
        """Test deleting location with proper permissions."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.delete(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/locations/{self.location.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check that location is soft deleted
        self.location.refresh_from_db()
        self.assertFalse(self.location.is_active)
        
        # User2 should not be able to delete (only view permission on world)
        location2 = Location.objects.create(
            region=self.region,
            name='Test Location 2',
            location_type='shop',
            description='Another test location',
            general_mood='Test mood',
            size_scale='Small',
            accessibility='Easy access'
        )
        
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/locations/{location2.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_location_statistics(self):
        """Test location statistics endpoint."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/locations/{self.location.id}/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stats = response.data
        self.assertEqual(stats['location_name'], 'Test Location')
        self.assertEqual(stats['location_type'], 'city')
        self.assertEqual(stats['important_personalities_count'], 0)
        self.assertEqual(stats['services_available_count'], 0)
        self.assertEqual(stats['notable_features_count'], 0)
    
    def test_location_search(self):
        """Test location search functionality."""
        self.client.force_authenticate(user=self.user1)
        
        # Search by name
        response = self.client.get(f'/api/world/worlds/{self.world.id}/locations/search/?q=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Location')
        
        # Search by type
        response = self.client.get(f'/api/world/worlds/{self.world.id}/locations/search/?type=city')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['location_type'], 'city')
        
        # Search with no results
        response = self.client.get(f'/api/world/worlds/{self.world.id}/locations/search/?q=Nonexistent')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
        # Search without query parameters
        response = self.client.get(f'/api/world/worlds/{self.world.id}/locations/search/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_location_by_type(self):
        """Test location filtering by type."""
        self.client.force_authenticate(user=self.user1)
        
        # Create additional locations of different types
        Location.objects.create(
            region=self.region,
            name='Test Tavern',
            location_type='tavern',
            description='A test tavern',
            general_mood='Cozy',
            size_scale='Medium',
            accessibility='Easy access'
        )
        
        Location.objects.create(
            region=self.region,
            name='Test Shop',
            location_type='shop',
            description='A test shop',
            general_mood='Busy',
            size_scale='Small',
            accessibility='Easy access'
        )
        
        # Test filtering by city type
        response = self.client.get(f'/api/world/worlds/{self.world.id}/locations/type/city/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['location_type'], 'city')
        
        # Test filtering by tavern type
        response = self.client.get(f'/api/world/worlds/{self.world.id}/locations/type/tavern/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['location_type'], 'tavern')
        
        # Test invalid location type
        response = self.client.get(f'/api/world/worlds/{self.world.id}/locations/type/invalid/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_location_validation(self):
        """Test location data validation."""
        self.client.force_authenticate(user=self.user1)
        
        # Test invalid data
        invalid_data = {
            'name': '',  # Empty name
            'description': 'A' * 2001,  # Too long description
            'location_type': 'invalid_type'  # Invalid location type
        }
        
        response = self.client.post(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/locations/create/', invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('description', response.data)
        self.assertIn('location_type', response.data)
    
    def test_location_unique_constraints(self):
        """Test location name uniqueness within region."""
        self.client.force_authenticate(user=self.user1)
        
        # Try to create location with same name
        location_data = {
            'name': 'Test Location',  # Same name as existing location
            'location_type': 'shop',
            'description': 'Another test location',
            'general_mood': 'Test mood',
            'size_scale': 'Small',
            'accessibility': 'Easy access'
        }
        
        response = self.client.post(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/locations/create/', location_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_location_json_fields(self):
        """Test that JSON fields are properly handled."""
        self.client.force_authenticate(user=self.user1)
        
        location_data = {
            'name': 'JSON Test Location',
            'location_type': 'city',
            'description': 'Testing JSON fields in locations',
            'general_mood': 'Complex',
            'size_scale': 'Large',
            'accessibility': 'Well-connected',
            'important_personalities': [
                {
                    'name': 'Mayor',
                    'role': 'City Leader',
                    'importance': 9,
                    'description': 'Elected city mayor'
                },
                {
                    'name': 'Guard Captain',
                    'role': 'Security',
                    'importance': 8,
                    'description': 'Head of city guard'
                }
            ],
            'services_available': [
                {
                    'type': 'accommodation',
                    'name': 'Luxury Inn',
                    'price': '5 gold per night',
                    'available': True
                },
                {
                    'type': 'food',
                    'name': 'Fine Dining',
                    'price': '2 gold per meal',
                    'available': True
                },
                {
                    'type': 'shopping',
                    'name': 'Market',
                    'price': 'Variable',
                    'available': True
                }
            ],
            'notable_features': [
                {
                    'name': 'Ancient Fountain',
                    'description': 'Magical healing properties',
                    'significance': 'City landmark'
                },
                {
                    'name': 'City Walls',
                    'description': 'Impenetrable defenses',
                    'significance': 'Military importance'
                }
            ],
            'secrets_hidden': [
                {
                    'name': 'Secret Passage',
                    'description': 'Hidden tunnel network',
                    'access': 'Difficult to find'
                }
            ],
            'encounters_possible': [
                {
                    'name': 'Street Thieves',
                    'type': 'combat',
                    'frequency': 'common',
                    'description': 'Pickpockets and muggers'
                }
            ],
            'items_treasures': [
                {
                    'name': 'Mayor\'s Signet Ring',
                    'type': 'magical',
                    'value': 'Priceless',
                    'location': 'Mayor\'s office'
                }
            ],
            'defenses_security': [
                {
                    'name': 'City Guard',
                    'type': 'military',
                    'size': 100,
                    'description': 'Well-trained city defenders'
                }
            ],
            'population_demographics': {
                'size': 5000,
                'composition': {
                    'humans': 60,
                    'elves': 20,
                    'dwarves': 15,
                    'others': 5
                },
                'wealth_distribution': 'Mixed'
            },
            'economic_activity': [
                {
                    'type': 'trade',
                    'description': 'Major trading hub',
                    'importance': 'high'
                },
                {
                    'type': 'crafting',
                    'description': 'Skilled artisans',
                    'importance': 'medium'
                }
            ],
            'connections_travel': [
                {
                    'type': 'road',
                    'destination': 'Capital City',
                    'distance': '50 miles',
                    'condition': 'Good'
                }
            ],
            'rumors_information': [
                {
                    'topic': 'Missing Merchants',
                    'credibility': 'medium',
                    'description': 'Merchants disappearing on the road'
                }
            ],
            'seasonal_changes': [
                {
                    'season': 'Winter',
                    'effect': 'Snow-covered streets',
                    'impact': 'Reduced travel'
                }
            ],
            'current_events': [
                {
                    'name': 'Festival Preparation',
                    'type': 'celebration',
                    'ongoing': True,
                    'description': 'Preparing for annual festival'
                }
            ],
            'quest_opportunities': [
                {
                    'name': 'Guard the Caravan',
                    'type': 'escort',
                    'difficulty': 'medium',
                    'reward': '50 gold'
                }
            ]
        }
        
        response = self.client.post(f'/api/world/worlds/{self.world.id}/regions/{self.region.id}/locations/create/', location_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that JSON fields were saved correctly
        location = Location.objects.get(name='JSON Test Location')
        self.assertEqual(len(location.important_personalities), 2)
        self.assertEqual(location.important_personalities[0]['name'], 'Mayor')
        self.assertEqual(len(location.services_available), 3)
        self.assertEqual(location.services_available[0]['type'], 'accommodation')
        self.assertEqual(len(location.notable_features), 2)
        self.assertEqual(location.notable_features[0]['name'], 'Ancient Fountain')
        self.assertEqual(len(location.secrets_hidden), 1)
        self.assertEqual(location.secrets_hidden[0]['name'], 'Secret Passage')
        self.assertEqual(len(location.encounters_possible), 1)
        self.assertEqual(location.encounters_possible[0]['name'], 'Street Thieves')
        self.assertEqual(len(location.items_treasures), 1)
        self.assertEqual(location.items_treasures[0]['name'], 'Mayor\'s Signet Ring')
        self.assertEqual(len(location.defenses_security), 1)
        self.assertEqual(location.defenses_security[0]['name'], 'City Guard')
        self.assertEqual(location.population_demographics['size'], 5000)
        self.assertEqual(location.population_demographics['composition']['humans'], 60)
        self.assertEqual(len(location.economic_activity), 2)
        self.assertEqual(location.economic_activity[0]['type'], 'trade')
        self.assertEqual(len(location.connections_travel), 1)
        self.assertEqual(location.connections_travel[0]['type'], 'road')
        self.assertEqual(len(location.rumors_information), 1)
        self.assertEqual(location.rumors_information[0]['topic'], 'Missing Merchants')
        self.assertEqual(len(location.seasonal_changes), 1)
        self.assertEqual(location.seasonal_changes[0]['season'], 'Winter')
        self.assertEqual(len(location.current_events), 1)
        self.assertEqual(location.current_events[0]['name'], 'Festival Preparation')
        self.assertEqual(len(location.quest_opportunities), 1)
        self.assertEqual(location.quest_opportunities[0]['name'], 'Guard the Caravan') 