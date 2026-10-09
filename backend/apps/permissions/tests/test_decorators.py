"""
Tests for Permission Decorators and Mixins.
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import Http404
from django.core.exceptions import PermissionDenied
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import models

from apps.permissions.decorators import (
    require_permission,
    require_permission_api,
    permission_required,
    get_resource_instance
)
from apps.permissions.models.permission import Permission

User = get_user_model()


# Simple test models for permission testing
class TestWorld(models.Model):
    """Simple test model for world permissions."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    class Meta:
        app_label = 'permissions'
        db_table = 'test_world'
    
    def __str__(self):
        return self.name


class TestAdventure(models.Model):
    """Simple test model for adventure permissions."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    class Meta:
        app_label = 'permissions'
        db_table = 'test_adventure'
    
    def __str__(self):
        return self.name


class PermissionDecoratorTest(TestCase):
    """Test cases for permission decorators."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        
        self.user1 = User.objects.create_user(
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='test2@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create test resources using the actual world model
        from apps.world.models import World
        self.world = World.objects.create(
            name='Test World',
            description='A test world for permissions',
            general_mood='Mysterious'
        )
        
        # For adventure, we'll use a mock since the adventure app is not available
        self.adventure = None
    
    def test_get_resource_instance(self):
        """Test getting resource instances by type and ID."""
        # Test world resource
        world_instance = get_resource_instance('world', self.world.id)
        self.assertEqual(world_instance, self.world)
        
        # Test adventure resource - skip since adventure app is not available
        if self.adventure is not None:
            adventure_instance = get_resource_instance('adventure', self.adventure.id)
            self.assertEqual(adventure_instance, self.adventure)
        
        # Test invalid resource type
        invalid_instance = get_resource_instance('invalid', 1)
        self.assertIsNone(invalid_instance)
        
        # Test invalid resource ID
        invalid_id_instance = get_resource_instance('world', 99999)
        self.assertIsNone(invalid_id_instance)
    
    def test_require_permission_decorator(self):
        """Test the require_permission decorator."""
        # Create a test view function
        @require_permission('view', 'world', 'world_id')
        def test_view(request, world_id, world_instance=None):
            return Response({'message': f"Success: {world_id}"})
        
        # Create request with user who has permission
        request = self.factory.get(f'/world/{self.world.id}/')
        request.user = self.user1
        
        # Grant permission to user
        Permission.grant_permission(
            user=self.user1,
            resource=self.world,
            permission_type='view',
            granted_by=self.admin_user
        )
        
        # Test successful access
        response = test_view(request, world_id=self.world.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], f"Success: {self.world.id}")
    
    def test_require_permission_api_decorator(self):
        """Test the require_permission_api decorator."""
        # Create a test API view function
        @api_view(['GET'])
        @require_permission_api('view', 'world', 'world_id')
        def test_api_view(request, world_id, world_instance=None):
            return Response({'message': 'Success'})
        
        # Create request with user who has permission
        request = self.factory.get(f'/api/world/{self.world.id}/')
        request.user = self.user1
        
        # Grant permission to user
        Permission.grant_permission(
            user=self.user1,
            resource=self.world,
            permission_type='view',
            granted_by=self.admin_user
        )
        
        # Test successful access
        response = test_api_view(request, world_id=self.world.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Success')
    
    def test_permission_required_decorator(self):
        """Test the permission_required decorator."""
        # Create a test view function
        @permission_required('view', 'world', 'world_id')
        def test_view(request, world_id, world_instance=None):
            return f"Success: {world_id}"
        
        # Create request with user who has permission
        request = self.factory.get(f'/world/{self.world.id}/')
        request.user = self.user1
        
        # Grant permission to user
        Permission.grant_permission(
            user=self.user1,
            resource=self.world,
            permission_type='view',
            granted_by=self.admin_user
        )
        
        # Test successful access
        response = test_view(request, world_id=self.world.id)
        self.assertEqual(response, f"Success: {self.world.id}")
    
    def test_anonymous_user_permissions(self):
        """Test permission decorators with anonymous users."""
        # Create a test view function
        @require_permission_api('view', 'world', 'world_id')
        def test_view(request, world_id, world_instance=None):
            return Response({'message': 'Success'})
        
        # Create request with anonymous user
        request = self.factory.get(f'/world/{self.world.id}/')
        request.user = None
        
        # Test denied access for anonymous user
        response = test_view(request, world_id=self.world.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Permission denied')


class PermissionMixinTest(APITestCase):
    """Test cases for permission mixins."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user1 = User.objects.create_user(
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='test2@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create test resources using the actual world model
        from apps.world.models import World
        self.world = World.objects.create(
            name='Test World',
            description='A test world for permissions',
            general_mood='Mysterious'
        )
    
    def test_permission_required_mixin(self):
        """Test PermissionRequiredMixin."""
        from apps.permissions.decorators import PermissionRequiredMixin
        from django.views.generic import DetailView
        
        # Create a test view class
        from apps.world.models import World
        class TestWorldView(PermissionRequiredMixin, DetailView):
            model = World
            permission_type = 'view'
            resource_type = 'world'
            resource_lookup = 'pk'
            template_name = 'test.html'
        
        # Grant permission to user
        Permission.grant_permission(
            user=self.user1,
            resource=self.world,
            permission_type='view',
            granted_by=self.admin_user
        )
        
        # Test successful access
        view = TestWorldView()
        request = self.factory.get(f'/world/{self.world.id}/')
        request.user = self.user1
        view.request = request
        view.kwargs = {'pk': self.world.id}
        
        # Should not raise any exceptions
        try:
            view.dispatch(request, pk=self.world.id)
        except Exception as e:
            self.fail(f"PermissionRequiredMixin raised an exception: {e}")
    
    def test_drf_permission_required_mixin(self):
        """Test DRFPermissionRequiredMixin."""
        from apps.permissions.decorators import DRFPermissionRequiredMixin
        from rest_framework.viewsets import ModelViewSet
        
        # Create a test viewset class
        from apps.world.models import World
        class TestWorldViewSet(DRFPermissionRequiredMixin, ModelViewSet):
            model = World
            permission_type = 'view'
            resource_type = 'world'
            resource_lookup = 'pk'
        
        # Grant permission to user
        Permission.grant_permission(
            user=self.user1,
            resource=self.world,
            permission_type='view',
            granted_by=self.admin_user
        )
        
        # Test successful access
        viewset = TestWorldViewSet()
        viewset.request = self.client.request()
        viewset.request.user = self.user1
        viewset.action = 'retrieve'
        viewset.kwargs = {'pk': self.world.id}
        
        # Should not raise any exceptions
        try:
            viewset.check_permissions(viewset.request)
        except Exception as e:
            self.fail(f"DRFPermissionRequiredMixin raised an exception: {e}")
    
    def test_resource_permission_class(self):
        """Test ResourcePermission class."""
        from apps.permissions.decorators import ResourcePermission
        
        # Create permission instance
        permission = ResourcePermission()
        
        # Create mock view
        class MockView:
            action = 'retrieve'
            permission_type = 'view'
            resource_type = 'world'
            resource_lookup = 'pk'
            kwargs = {'pk': self.world.id}
        
        # Create mock request
        class MockRequest:
            user = self.user1
        
        # Grant permission to user
        Permission.grant_permission(
            user=self.user1,
            resource=self.world,
            permission_type='view',
            granted_by=self.admin_user
        )
        
        # Test successful permission check
        view = MockView()
        request = MockRequest()
        
        has_perm = permission.has_permission(request, view)
        self.assertTrue(has_perm)
    
    def test_resource_permission_class_denied(self):
        """Test ResourcePermission class with denied access."""
        from apps.permissions.decorators import ResourcePermission
        
        # Create permission instance
        permission = ResourcePermission()
        
        # Create mock view
        class MockView:
            action = 'retrieve'
            permission_type = 'edit'
            resource_type = 'world'
            resource_lookup = 'pk'
            kwargs = {'pk': self.world.id}
        
        # Create mock request
        class MockRequest:
            user = self.user1
        
        # Don't grant any permissions
        
        # Test denied permission check
        view = MockView()
        request = MockRequest()
        
        has_perm = permission.has_permission(request, view)
        self.assertFalse(has_perm)
    
    def test_resource_permission_class_list_action(self):
        """Test ResourcePermission class with list action (should be allowed)."""
        from apps.permissions.decorators import ResourcePermission
        
        # Create permission instance
        permission = ResourcePermission()
        
        # Create mock view
        class MockView:
            action = 'list'
            permission_type = 'view'
            resource_type = 'world'
            resource_lookup = 'pk'
            kwargs = {}
        
        # Create mock request
        class MockRequest:
            user = self.user1
        
        # Test list action (should be allowed without resource check)
        view = MockView()
        request = MockRequest()
        
        has_perm = permission.has_permission(request, view)
        self.assertTrue(has_perm) 