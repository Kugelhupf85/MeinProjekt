"""
Test Helper Utilities for Core User Tests.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.core_user.models import SecurityQuestion, UserSecurityAnswer

User = get_user_model()


class BaseTestCase(TestCase):
    """
    Base test case with common setup for core user tests.
    """
    
    def setUp(self):
        """
        Set up test data.
        """
        self.client = APIClient()
        
        # Create test user
        self.user_data = {
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'TestPass123!'
        }
        
        self.user = User.objects.create_user(**self.user_data)
        # Make sure user is email verified for login tests
        self.user.is_email_verified = True
        self.user.save()
        
        # Create admin user
        self.admin_data = {
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'password': 'AdminPass123!'
        }
        
        self.admin_user = User.objects.create_superuser(**self.admin_data)
        
        # Create security questions
        self.security_questions = []
        questions_data = [
            'Wie heißt Ihr erster Pen-and-Paper-Charakter?',
            'Welches war Ihr erstes Rollenspielsystem?',
            'Wie heißt Ihr Lieblings-Spielmeister/DM?'
        ]
        
        for question_text in questions_data:
            question = SecurityQuestion.objects.create(
                question_text=question_text,
                is_active=True
            )
            self.security_questions.append(question)
    
    def get_jwt_tokens(self, user):
        """
        Get JWT tokens for a user.
        """
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
    
    def authenticate_user(self, user):
        """
        Authenticate a user with JWT token.
        """
        tokens = self.get_jwt_tokens(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        return tokens
    
    def create_security_answers(self, user, answers_data=None):
        """
        Create security answers for a user.
        
        Args:
            user: User instance
            answers_data: List of dicts with 'question' and 'answer' keys
        """
        if answers_data is None:
            answers_data = [
                {'question': self.security_questions[0], 'answer': 'Gandalf'},
                {'question': self.security_questions[1], 'answer': 'DSA'},
                {'question': self.security_questions[2], 'answer': 'Tolkien'}
            ]
        
        created_answers = []
        for data in answers_data:
            security_answer = UserSecurityAnswer.objects.create(
                user=user,
                question=data['question']
            )
            security_answer.set_answer(data['answer'])
            created_answers.append(security_answer)
        
        return created_answers
    
    def logout_user(self):
        """
        Clear authentication credentials.
        """
        self.client.credentials()


class AuthTestMixin:
    """
    Mixin for authentication-related tests.
    """
    
    def assert_jwt_response(self, response):
        """
        Assert that response contains valid JWT tokens.
        """
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        
        # Tokens should be non-empty strings
        self.assertTrue(response.data['tokens']['access'])
        self.assertTrue(response.data['tokens']['refresh'])
    
    def assert_user_data(self, response_data, user):
        """
        Assert that response contains correct user data.
        """
        self.assertEqual(response_data['id'], user.id)
        self.assertEqual(response_data['email'], user.email)
        self.assertEqual(response_data['full_name'], user.full_name)


class DatabaseTestMixin:
    """
    Mixin for database-related tests.
    """
    
    def assert_user_exists(self, email):
        """
        Assert that a user exists in the database.
        """
        self.assertTrue(User.objects.filter(email=email).exists())
    
    def assert_user_not_exists(self, email):
        """
        Assert that a user does not exist in the database.
        """
        self.assertFalse(User.objects.filter(email=email).exists())
    
    def assert_security_answers_count(self, user, count):
        """
        Assert the number of security answers for a user.
        """
        self.assertEqual(user.security_answers.count(), count)
    
    def refresh_user(self, user):
        """
        Refresh user instance from database.
        """
        return User.objects.get(pk=user.pk) 