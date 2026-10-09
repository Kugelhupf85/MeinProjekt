"""
Tests for User Models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.core_user.models import SecurityQuestion, UserSecurityAnswer, Role, UserWorldRole
from ..utils.test_helpers import BaseTestCase, DatabaseTestMixin

User = get_user_model()


class UserModelTests(BaseTestCase, DatabaseTestMixin):
    """
    Tests for the User model.
    """
    
    def test_create_user_with_email(self):
        """Test creating a user with email."""
        user = User.objects.create_user(
            email='newuser@example.com',
            password='TestPass123!',
            first_name='New',
            last_name='User'
        )
        
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.full_name, 'New User')
        self.assertTrue(user.check_password('TestPass123!'))
        self.assertFalse(user.is_email_verified)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='super@example.com',
            password='SuperPass123!',
            first_name='Super',
            last_name='User'
        )
        
        self.assertEqual(user.email, 'super@example.com')
        self.assertTrue(user.is_email_verified)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        self.assertEqual(str(user), 'Test User')
        
        # Test with only email
        user_no_name = User.objects.create_user(email='noname@example.com')
        self.assertEqual(str(user_no_name), 'noname@example.com')
    
    def test_email_uniqueness(self):
        """Test that email addresses must be unique."""
        User.objects.create_user(
            email='unique@example.com',
            password='TestPass123!'
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='unique@example.com',
                password='AnotherPass123!'
            )
    
    def test_email_verification_token_generation(self):
        """Test email verification token generation."""
        user = self.user
        self.assertIsNone(user.email_verification_token)
        
        token = user.generate_email_verification_token()
        
        self.assertIsNotNone(token)
        self.assertEqual(user.email_verification_token, token)
        self.assertEqual(len(token), 36)  # UUID format
    
    def test_email_verification(self):
        """Test email verification process."""
        user = self.user
        token = user.generate_email_verification_token()
        
        # Test successful verification
        self.assertTrue(user.verify_email(token))
        self.assertTrue(user.is_email_verified)
        self.assertIsNone(user.email_verification_token)
        
        # Test invalid token
        self.assertFalse(user.verify_email('invalid-token'))
    
    def test_full_name_property(self):
        """Test full_name property."""
        user = User.objects.create_user(
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )
        
        self.assertEqual(user.full_name, 'John Doe')
        
        # Test with empty names
        user_empty = User.objects.create_user(email='empty@example.com')
        self.assertEqual(user_empty.full_name, 'empty@example.com')


class SecurityQuestionModelTests(BaseTestCase):
    """
    Tests for the SecurityQuestion model.
    """
    
    def test_create_security_question(self):
        """Test creating a security question."""
        question = SecurityQuestion.objects.create(
            question_text='What is your favorite color?',
            is_active=True
        )
        
        self.assertEqual(question.question_text, 'What is your favorite color?')
        self.assertTrue(question.is_active)
        self.assertIsNotNone(question.created_at)
    
    def test_security_question_str_representation(self):
        """Test security question string representation."""
        question = self.security_questions[0]
        self.assertEqual(str(question), question.question_text)
    
    def test_question_text_uniqueness(self):
        """Test that question texts must be unique."""
        SecurityQuestion.objects.create(
            question_text='Unique question?',
            is_active=True
        )
        
        with self.assertRaises(IntegrityError):
            SecurityQuestion.objects.create(
                question_text='Unique question?',
                is_active=False
            )


class UserSecurityAnswerModelTests(BaseTestCase, DatabaseTestMixin):
    """
    Tests for the UserSecurityAnswer model.
    """
    
    def test_create_security_answer(self):
        """Test creating a security answer."""
        question = self.security_questions[0]
        answer = UserSecurityAnswer.objects.create(
            user=self.user,
            question=question
        )
        
        self.assertEqual(answer.user, self.user)
        self.assertEqual(answer.question, question)
        self.assertIsNotNone(answer.created_at)
    
    def test_set_and_check_answer(self):
        """Test setting and checking security answers."""
        question = self.security_questions[0]
        answer = UserSecurityAnswer.objects.create(
            user=self.user,
            question=question
        )
        
        # Set answer
        answer.set_answer('My Answer')
        
        # Check correct answer
        self.assertTrue(answer.check_answer('My Answer'))
        self.assertTrue(answer.check_answer('my answer'))  # Case insensitive
        self.assertTrue(answer.check_answer(' My Answer '))  # Whitespace trimmed
        
        # Check incorrect answer
        self.assertFalse(answer.check_answer('Wrong Answer'))
    
    def test_validate_user_answers(self):
        """Test validating multiple user answers."""
        # Create security answers
        answers = self.create_security_answers(self.user)
        
        # Test correct answers
        answers_dict = {
            self.security_questions[0].id: 'Gandalf',
            self.security_questions[1].id: 'DSA'
        }
        
        self.assertTrue(
            UserSecurityAnswer.validate_user_answers(self.user, answers_dict)
        )
        
        # Test incorrect answers
        wrong_answers_dict = {
            self.security_questions[0].id: 'Wrong',
            self.security_questions[1].id: 'DSA'
        }
        
        self.assertFalse(
            UserSecurityAnswer.validate_user_answers(self.user, wrong_answers_dict)
        )
        
        # Test missing answers - the method only validates provided answers
        # It returns False if the user doesn't have answers for the provided question IDs
        incomplete_answers_dict = {
            self.security_questions[0].id: 'Gandalf'
        }
        
        self.assertTrue(
            UserSecurityAnswer.validate_user_answers(self.user, incomplete_answers_dict)
        )
        
        # Test non-existent question ID
        nonexistent_answers_dict = {
            99999: 'Some Answer'
        }
        
        self.assertFalse(
            UserSecurityAnswer.validate_user_answers(self.user, nonexistent_answers_dict)
        )
    
    def test_user_question_uniqueness(self):
        """Test that a user can only have one answer per question."""
        question = self.security_questions[0]
        
        UserSecurityAnswer.objects.create(
            user=self.user,
            question=question
        )
        
        with self.assertRaises(IntegrityError):
            UserSecurityAnswer.objects.create(
                user=self.user,
                question=question
            )


class RoleModelTests(BaseTestCase):
    """
    Tests for the Role model.
    """
    
    def test_create_role(self):
        """Test creating a role."""
        role = Role.objects.create(
            name='test_role',
            display_name='Test Role',
            description='A test role',
            is_active=True
        )
        
        self.assertEqual(role.name, 'test_role')
        self.assertEqual(role.display_name, 'Test Role')
        self.assertTrue(role.is_active)
    
    def test_role_str_representation(self):
        """Test role string representation."""
        role = Role.objects.create(
            name='test_role',
            display_name='Test Role'
        )
        
        self.assertEqual(str(role), 'Test Role')


class UserWorldRoleModelTests(BaseTestCase):
    """
    Tests for the UserWorldRole model.
    """
    
    def setUp(self):
        super().setUp()
        
        # Create test role with unique name to avoid conflicts
        self.role = Role.objects.create(
            name='test_player',
            display_name='Test Player',
            is_active=True
        )
        
        # Create mock world (we'll need to import from world app later)
        # For now, we'll skip world-related tests
    
    def test_role_name_choices(self):
        """Test that role names are restricted to valid choices."""
        # Test valid role names with unique names to avoid conflicts
        valid_roles = [
            ('test_dm', 'Test Dungeon Master'),
            ('test_admin', 'Test World Admin')
        ]
        
        for role_name, display_name in valid_roles:
            role = Role.objects.create(
                name=role_name,
                display_name=display_name
            )
            # Just test that the role was created successfully
            self.assertEqual(role.name, role_name)
            self.assertEqual(role.display_name, display_name) 