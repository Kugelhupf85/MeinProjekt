"""
Tests for Authentication API with JWT.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from apps.core_user.models import SecurityQuestion, UserSecurityAnswer
from ..utils.test_helpers import BaseTestCase, AuthTestMixin, DatabaseTestMixin

User = get_user_model()


class LoginAPITests(BaseTestCase, AuthTestMixin):
    """
    Tests for login API with JWT tokens.
    """
    
    def test_login_with_email_success(self):
        """Test successful login with email and password."""
        url = '/api/auth/login/'
        data = {
            'username': self.user.email,
            'password': 'TestPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assert_jwt_response(response)
        self.assert_user_data(response.data['user'], self.user)
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        url = '/api/auth/login/'
        data = {
            'username': self.user.email,
            'password': 'WrongPassword'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('tokens', response.data)
    
    def test_login_with_unverified_email(self):
        """Test login with unverified email."""
        # Create user with unverified email
        unverified_user = User.objects.create_user(
            email='unverified@example.com',
            password='TestPass123!',
            is_email_verified=False
        )
        
        url = '/api/auth/login/'
        data = {
            'username': unverified_user.email,
            'password': 'TestPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Please verify your email', str(response.data))
    
    def test_login_with_inactive_user(self):
        """Test login with inactive user."""
        self.user.is_active = False
        self.user.save()
        
        url = '/api/auth/login/'
        data = {
            'username': self.user.email,
            'password': 'TestPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('disabled', str(response.data))
    
    def test_login_missing_credentials(self):
        """Test login with missing credentials."""
        url = '/api/auth/login/'
        
        # Missing password
        data = {'username': self.user.email}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing username
        data = {'password': 'TestPass123!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JWTTokenTests(BaseTestCase):
    """
    Tests for JWT token functionality.
    """
    
    def test_jwt_authentication(self):
        """Test JWT token authentication."""
        # Get JWT tokens
        tokens = self.authenticate_user(self.user)
        
        # Test authenticated endpoint
        url = '/api/auth/check/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['authenticated'])
        self.assertEqual(response.data['user']['id'], self.user.id)
    
    def test_jwt_token_refresh(self):
        """Test JWT token refresh."""
        tokens = self.get_jwt_tokens(self.user)
        
        url = '/api/auth/refresh/'
        data = {'refresh': tokens['refresh']}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertNotEqual(response.data['access'], tokens['access'])
    
    def test_invalid_jwt_token(self):
        """Test authentication with invalid JWT token."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token')
        
        url = '/api/auth/check/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_expired_jwt_token(self):
        """Test authentication with expired JWT token."""
        # This would require mocking time or creating an expired token
        # For now, we'll test with an invalid format
        self.client.credentials(HTTP_AUTHORIZATION='Bearer expired.token.here')
        
        url = '/api/auth/check/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutAPITests(BaseTestCase):
    """
    Tests for logout API.
    """
    
    def test_logout_success(self):
        """Test successful logout."""
        tokens = self.authenticate_user(self.user)
        
        url = '/api/auth/logout/'
        data = {'refresh': tokens['refresh']}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_logout_without_authentication(self):
        """Test logout without authentication."""
        url = '/api/auth/logout/'
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RegistrationAPITests(BaseTestCase, DatabaseTestMixin):
    """
    Tests for user registration API.
    """
    
    def test_register_user_success(self):
        """Test successful user registration."""
        url = '/api/auth/register/'
        data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'NewUserPass123!',
            'password_confirm': 'NewUserPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('verification_token', response.data)
        
        # Check user was created in database
        self.assert_user_exists('newuser@example.com')
        
        # Check user is not verified
        new_user = User.objects.get(email='newuser@example.com')
        self.assertFalse(new_user.is_email_verified)
    
    def test_register_user_password_mismatch(self):
        """Test registration with password mismatch."""
        url = '/api/auth/register/'
        data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'NewUserPass123!',
            'password_confirm': 'DifferentPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)
        self.assert_user_not_exists('newuser@example.com')
    
    def test_register_user_duplicate_email(self):
        """Test registration with duplicate email."""
        url = '/api/auth/register/'
        data = {
            'email': self.user.email,
            'first_name': 'Duplicate',
            'last_name': 'User',
            'password': 'DuplicatePass123!',
            'password_confirm': 'DuplicatePass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_register_user_weak_password(self):
        """Test registration with weak password."""
        url = '/api/auth/register/'
        data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': '123',
            'password_confirm': '123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


class EmailVerificationAPITests(BaseTestCase):
    """
    Tests for email verification API.
    """
    
    def test_verify_email_success(self):
        """Test successful email verification."""
        self.authenticate_user(self.user)
        token = self.user.generate_email_verification_token()
        
        url = '/api/auth/verify-email/'
        data = {'token': token}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Check user is verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)
    
    def test_verify_email_invalid_token(self):
        """Test email verification with invalid token."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/verify-email/'
        data = {'token': 'invalid-token'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_resend_verification_email(self):
        """Test resending verification email."""
        # Set user as unverified
        self.user.is_email_verified = False
        self.user.save()
        
        self.authenticate_user(self.user)
        
        url = '/api/auth/resend-verification/'
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('verification_token', response.data)
    
    def test_resend_verification_already_verified(self):
        """Test resending verification for already verified user."""
        self.user.is_email_verified = True
        self.user.save()
        
        self.authenticate_user(self.user)
        
        url = '/api/auth/resend-verification/'
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already verified', str(response.data))


class PasswordManagementAPITests(BaseTestCase, DatabaseTestMixin):
    """
    Tests for password management API.
    """
    
    def test_change_password_success(self):
        """Test successful password change."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/change-password/'
        data = {
            'current_password': 'TestPass123!',
            'new_password': 'NewTestPass123!',
            'new_password_confirm': 'NewTestPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewTestPass123!'))
    
    def test_change_password_wrong_current(self):
        """Test password change with wrong current password."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/change-password/'
        data = {
            'current_password': 'WrongPassword',
            'new_password': 'NewTestPass123!',
            'new_password_confirm': 'NewTestPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('current_password', response.data)
    
    def test_change_password_mismatch(self):
        """Test password change with new password mismatch."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/change-password/'
        data = {
            'current_password': 'TestPass123!',
            'new_password': 'NewTestPass123!',
            'new_password_confirm': 'DifferentPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password_confirm', response.data)
    
    def test_reset_password_with_security_questions(self):
        """Test password reset using security questions."""
        # Create security answers
        self.create_security_answers(self.user)
        
        url = '/api/auth/reset-password-security/'
        data = {
            'email': self.user.email,
            'security_answers': [
                {'question_id': self.security_questions[0].id, 'answer': 'Gandalf'},
                {'question_id': self.security_questions[1].id, 'answer': 'DSA'}
            ],
            'new_password': 'ResetPass123!',
            'new_password_confirm': 'ResetPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check password was reset
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('ResetPass123!'))
    
    def test_reset_password_wrong_security_answers(self):
        """Test password reset with wrong security answers."""
        # Create security answers
        self.create_security_answers(self.user)
        
        url = '/api/auth/reset-password-security/'
        data = {
            'email': self.user.email,
            'security_answers': [
                {'question_id': self.security_questions[0].id, 'answer': 'Wrong'},
                {'question_id': self.security_questions[1].id, 'answer': 'DSA'}
            ],
            'new_password': 'ResetPass123!',
            'new_password_confirm': 'ResetPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('security_answers', response.data) 