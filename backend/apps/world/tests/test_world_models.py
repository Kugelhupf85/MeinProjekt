"""
Tests for World Models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.world.models import World, WorldAPIKeys, WorldParty, WorldPartyMembership
from apps.permissions.models.permission import Permission

User = get_user_model()


class WorldModelTest(TestCase):
    """Test cases for World model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.world = World.objects.create(
            name='Test World',
            description='A test world for testing',
            general_mood='Mysterious'
        )
    
    def test_world_creation(self):
        """Test creating a world."""
        self.assertEqual(self.world.name, 'Test World')
        self.assertEqual(self.world.description, 'A test world for testing')
        self.assertEqual(self.world.general_mood, 'Mysterious')
        self.assertTrue(self.world.is_active)
        self.assertIsNotNone(self.world.entity_id)
        self.assertTrue(self.world.entity_id.startswith('WLD-'))
    
    def test_world_pill_generation(self):
        """Test pill generation for world."""
        pill = self.world.generate_pill()
        self.assertIsNotNone(pill)
        self.assertEqual(pill['name'], 'Test World')
        self.assertEqual(pill['entity_id'], self.world.entity_id)
    
    def test_world_properties(self):
        """Test world properties."""
        self.assertEqual(self.world.region_count, 0)
        self.assertEqual(self.world.total_locations, 0)


class WorldAPIKeysModelTest(TestCase):
    """Test cases for WorldAPIKeys model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.world = World.objects.create(
            name='Test World',
            description='A test world for testing',
            general_mood='Mysterious'
        )
        
        # WorldAPIKeys should be automatically created via signal
        self.api_keys = WorldAPIKeys.objects.get(world=self.world)
    
    def test_api_keys_creation(self):
        """Test that API keys are automatically created."""
        self.assertIsNotNone(self.api_keys)
        self.assertEqual(self.api_keys.world, self.world)
        self.assertEqual(self.api_keys.openai_status, 'not_configured')
        self.assertEqual(self.api_keys.anthropic_status, 'not_configured')
    
    def test_api_keys_provider_management(self):
        """Test API key provider management."""
        # Test marking provider as configured
        self.api_keys.mark_provider_configured('openai')
        self.assertEqual(self.api_keys.openai_status, 'configured')
        self.assertIsNotNone(self.api_keys.openai_last_validated)
        
        # Test marking provider as invalid
        self.api_keys.mark_provider_invalid('anthropic')
        self.assertEqual(self.api_keys.anthropic_status, 'invalid')
        
        # Test getting configured providers
        providers = self.api_keys.get_configured_providers()
        self.assertIn('openai', providers)
        self.assertNotIn('anthropic', providers)
    
    def test_api_keys_usage_tracking(self):
        """Test API key usage tracking."""
        # Test incrementing usage
        self.api_keys.increment_usage('openai')
        self.assertEqual(self.api_keys.usage_statistics['openai']['requests_today'], 1)
        
        # Test resetting daily usage
        self.api_keys.reset_daily_usage()
        self.assertEqual(self.api_keys.usage_statistics['openai']['requests_today'], 0)
    
    def test_api_keys_provider_check(self):
        """Test checking if provider is configured."""
        self.assertFalse(self.api_keys.is_provider_configured('openai'))
        
        self.api_keys.mark_provider_configured('openai')
        self.assertTrue(self.api_keys.is_provider_configured('openai'))


class WorldPartyModelTest(TestCase):
    """Test cases for WorldParty model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.world = World.objects.create(
            name='Test World',
            description='A test world for testing',
            general_mood='Mysterious'
        )
        
        # WorldParty should be automatically created via signal
        self.party = WorldParty.objects.get(world=self.world)
    
    def test_party_creation(self):
        """Test that party is automatically created."""
        self.assertIsNotNone(self.party)
        self.assertEqual(self.party.world, self.world)
        self.assertEqual(self.party.name, f"Party of {self.world.name}")
        self.assertTrue(self.party.is_active)
        self.assertIsNotNone(self.party.entity_id)
        self.assertTrue(self.party.entity_id.startswith('WP-'))
    
    def test_party_properties(self):
        """Test party properties."""
        self.assertEqual(self.party.member_count, 0)
        self.assertFalse(self.party.is_full)
    
    def test_party_member_management(self):
        """Test party member management."""
        # Create a test user
        test_user = User.objects.create_user(
            email='member@example.com',
            password='testpass123'
        )
        
        # Create membership
        membership = WorldPartyMembership.objects.create(
            user=test_user,
            party=self.party,
            role='player',
            status='active'
        )
        
        # Test member count
        self.assertEqual(self.party.member_count, 1)
        
        # Test getting members
        players = self.party.get_players()
        self.assertEqual(len(players), 1)
        self.assertEqual(players[0].user, test_user)
        
        # Test getting active members
        active_members = self.party.get_active_members()
        self.assertEqual(len(active_members), 1)
        self.assertEqual(active_members[0].user, test_user)


class WorldPartyMembershipModelTest(TestCase):
    """Test cases for WorldPartyMembership model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.world = World.objects.create(
            name='Test World',
            description='A test world for testing',
            general_mood='Mysterious'
        )
        
        self.party = WorldParty.objects.get(world=self.world)
        
        self.member = User.objects.create_user(
            email='member@example.com',
            password='testpass123'
        )
    
    def test_membership_creation(self):
        """Test creating party membership."""
        membership = WorldPartyMembership.objects.create(
            user=self.member,
            party=self.party,
            role='player',
            status='invited'
        )
        
        self.assertEqual(membership.user, self.member)
        self.assertEqual(membership.party, self.party)
        self.assertEqual(membership.role, 'player')
        self.assertEqual(membership.status, 'invited')
    
    def test_membership_role_permissions(self):
        """Test that permissions are set based on role."""
        # Test player role
        membership = WorldPartyMembership.objects.create(
            user=self.member,
            party=self.party,
            role='player',
            status='active'
        )
        
        self.assertFalse(membership.can_invite_members)
        self.assertFalse(membership.can_manage_campaigns)
        self.assertFalse(membership.can_edit_party)
        self.assertFalse(membership.can_change_roles)
        self.assertFalse(membership.can_remove_members)
        self.assertFalse(membership.can_access_api_keys)
        
        # Test DM role
        membership.role = 'dungeon_master'
        membership.save()
        
        self.assertTrue(membership.can_invite_members)
        self.assertTrue(membership.can_manage_campaigns)
        self.assertTrue(membership.can_edit_party)
        self.assertTrue(membership.can_change_roles)
        self.assertTrue(membership.can_remove_members)
        self.assertTrue(membership.can_access_api_keys)
    
    def test_membership_role_changes(self):
        """Test membership role change methods."""
        membership = WorldPartyMembership.objects.create(
            user=self.member,
            party=self.party,
            role='player',
            status='active'
        )
        
        # Test promotion to DM
        membership.promote_to_dm()
        self.assertEqual(membership.role, 'dungeon_master')
        self.assertTrue(membership.can_access_api_keys)
        
        # Test demotion to player
        membership.demote_to_player()
        self.assertEqual(membership.role, 'player')
        self.assertFalse(membership.can_access_api_keys)
        
        # Test making co-DM
        membership.make_co_dm()
        self.assertEqual(membership.role, 'co_dm')
        self.assertTrue(membership.can_access_api_keys)
    
    def test_membership_status_changes(self):
        """Test membership status change methods."""
        membership = WorldPartyMembership.objects.create(
            user=self.member,
            party=self.party,
            role='player',
            status='invited'
        )
        
        # Test activation
        membership.activate()
        self.assertEqual(membership.status, 'active')
        
        # Test deactivation
        membership.deactivate()
        self.assertEqual(membership.status, 'inactive')
        
        # Test banning
        membership.ban()
        self.assertEqual(membership.status, 'banned')


class WorldPermissionIntegrationTest(TestCase):
    """Test cases for World-Permission integration."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.world = World.objects.create(
            name='Test World',
            description='A test world for testing',
            general_mood='Mysterious'
        )
        
        self.party = WorldParty.objects.get(world=self.world)
    
    def test_world_creator_permissions(self):
        """Test that world creator gets admin permissions."""
        # Create world with creator
        creator = User.objects.create_user(
            email='creator@example.com',
            password='testpass123'
        )
        
        world_with_creator = World.objects.create(
            name='Creator World',
            description='A world with creator',
            general_mood='Mysterious',
            created_by=creator
        )
        
        # Check that creator has admin permission
        self.assertTrue(Permission.has_permission(creator, world_with_creator, 'admin'))
    
    def test_party_member_permissions(self):
        """Test that party members get appropriate permissions."""
        member = User.objects.create_user(
            email='member@example.com',
            password='testpass123'
        )
        
        # Create membership with DM role
        membership = WorldPartyMembership.objects.create(
            user=member,
            party=self.party,
            role='dungeon_master',
            status='active'
        )
        
        # Check that DM has admin permission
        self.assertTrue(Permission.has_permission(member, self.world, 'admin'))
        
        # Change role to player
        membership.role = 'player'
        membership.save()
        
        # Check that player doesn't have admin permission
        self.assertFalse(Permission.has_permission(member, self.world, 'admin')) 