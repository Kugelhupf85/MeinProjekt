"""
Tests for Profile Management API.
"""
from rest_framework import status
from django.contrib.auth import get_user_model
from ..utils.test_helpers import BaseTestCase, DatabaseTestMixin

User = get_user_model()


class ProfileAPITests(BaseTestCase, DatabaseTestMixin):
    """
    Tests for user profile API.
    """
    
    def test_get_profile_authenticated(self):
        """Test getting user profile when authenticated."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/profile/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['full_name'], self.user.full_name)
        self.assertIn('created_at', response.data)
        self.assertIn('updated_at', response.data)
    
    def test_get_profile_unauthenticated(self):
        """Test getting user profile when not authenticated."""
        url = '/api/auth/profile/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile_success(self):
        """Test successful profile update."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/profile/update/'
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        
        # Check database was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
    
    def test_update_profile_empty_names(self):
        """Test profile update with empty names."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/profile/update/'
        data = {
            'first_name': '',
            'last_name': 'Name'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data)
    
    def test_update_profile_partial(self):
        """Test partial profile update."""
        self.authenticate_user(self.user)
        original_last_name = self.user.last_name
        
        url = '/api/auth/profile/update/'
        data = {
            'first_name': 'OnlyFirst'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check only first name was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'OnlyFirst')
        self.assertEqual(self.user.last_name, original_last_name)
    
    def test_update_profile_unauthenticated(self):
        """Test profile update when not authenticated."""
        url = '/api/auth/profile/update/'
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminUserManagementAPITests(BaseTestCase, DatabaseTestMixin):
    """
    Tests for admin user management API.
    """
    
    def test_list_users_as_admin(self):
        """Test listing users as admin."""
        self.authenticate_user(self.admin_user)
        
        url = '/api/auth/users/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 2)  # At least test user and admin
    
    def test_list_users_as_regular_user(self):
        """Test listing users as regular user (should fail)."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/users/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_users_unauthenticated(self):
        """Test listing users when not authenticated."""
        url = '/api/auth/users/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_user_detail_as_admin(self):
        """Test getting user details as admin."""
        self.authenticate_user(self.admin_user)
        
        url = f'/api/auth/users/{self.user.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['email'], self.user.email)
    
    def test_get_user_detail_as_regular_user(self):
        """Test getting user details as regular user (should fail)."""
        self.authenticate_user(self.user)
        
        url = f'/api/auth/users/{self.admin_user.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_nonexistent_user_detail(self):
        """Test getting details of nonexistent user."""
        self.authenticate_user(self.admin_user)
        
        url = '/api/auth/users/99999/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_toggle_user_active_status(self):
        """Test toggling user active status as admin."""
        self.authenticate_user(self.admin_user)
        original_status = self.user.is_active
        
        url = f'/api/auth/users/{self.user.id}/toggle-active/'
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_active', response.data)
        
        # Check database was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.is_active, not original_status)
    
    def test_toggle_user_active_as_regular_user(self):
        """Test toggling user active status as regular user (should fail)."""
        self.authenticate_user(self.user)
        
        url = f'/api/auth/users/{self.admin_user.id}/toggle-active/'
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_list_search(self):
        """Test user list with search functionality."""
        # Create additional test user
        search_user = User.objects.create_user(
            email='searchable@example.com',
            first_name='Searchable',
            last_name='User',
            password='SearchPass123!'
        )
        
        self.authenticate_user(self.admin_user)
        
        # Search by email
        url = '/api/auth/users/?search=searchable'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], 'searchable@example.com')
        
        # Search by first name
        url = '/api/auth/users/?search=Searchable'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_user_list_ordering(self):
        """Test user list ordering."""
        self.authenticate_user(self.admin_user)
        
        url = '/api/auth/users/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that results are ordered by date_joined descending
        results = response.data['results']
        if len(results) > 1:
            for i in range(len(results) - 1):
                first_date = results[i]['date_joined']
                second_date = results[i + 1]['date_joined']
                self.assertGreaterEqual(first_date, second_date) 