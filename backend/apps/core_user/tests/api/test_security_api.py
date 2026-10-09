"""
Tests for Security Management API.
"""
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.core_user.models import SecurityQuestion, UserSecurityAnswer
from ..utils.test_helpers import BaseTestCase, DatabaseTestMixin

User = get_user_model()


class SecurityQuestionAPITests(BaseTestCase):
    """
    Tests for security questions API.
    """
    
    def test_list_security_questions_public(self):
        """Test listing security questions (public endpoint)."""
        url = '/api/auth/security-questions/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 3)  # From setUp
        
        # Check question structure
        question = response.data['results'][0]
        self.assertIn('id', question)
        self.assertIn('question_text', question)
        self.assertNotIn('is_active', question)  # Should not expose internal fields
    
    def test_get_user_security_questions_for_reset(self):
        """Test getting security questions for password reset."""
        # Create security answers for user
        self.create_security_answers(self.user)
        
        url = f'/api/auth/user-security-questions/?email={self.user.email}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # User has 3 security answers
    
    def test_get_user_security_questions_no_email(self):
        """Test getting security questions without email parameter."""
        url = '/api/auth/user-security-questions/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email parameter is required', str(response.data))
    
    def test_get_user_security_questions_nonexistent_user(self):
        """Test getting security questions for nonexistent user."""
        url = '/api/auth/user-security-questions/?email=nonexistent@example.com'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Account not found', str(response.data))
    
    def test_get_user_security_questions_insufficient_answers(self):
        """Test getting security questions for user with insufficient answers."""
        # Create only one security answer (minimum is 2)
        answer = UserSecurityAnswer.objects.create(
            user=self.user,
            question=self.security_questions[0]
        )
        answer.set_answer('Test Answer')
        
        url = f'/api/auth/user-security-questions/?email={self.user.email}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not have enough security questions', str(response.data))


class UserSecurityAnswerAPITests(BaseTestCase, DatabaseTestMixin):
    """
    Tests for user security answers API.
    """
    
    def test_get_my_security_answers(self):
        """Test getting current user's security answers."""
        self.authenticate_user(self.user)
        self.create_security_answers(self.user)
        
        url = '/api/auth/my-security-answers/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Check answer structure (should not reveal actual answers)
        answer = response.data[0]
        self.assertIn('id', answer)
        self.assertIn('question', answer)
        self.assertIn('created_at', answer)
        self.assertNotIn('answer_hash', answer)  # Should not expose hash
    
    def test_get_my_security_answers_unauthenticated(self):
        """Test getting security answers when not authenticated."""
        url = '/api/auth/my-security-answers/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_set_security_answers_success(self):
        """Test successfully setting security answers."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/set-security-answers/'
        data = {
            'answers': [
                {'question_id': self.security_questions[0].id, 'answer': 'Gandalf'},
                {'question_id': self.security_questions[1].id, 'answer': 'DSA'},
                {'question_id': self.security_questions[2].id, 'answer': 'Tolkien'}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['count'], 3)
        
        # Check answers were created in database
        self.assert_security_answers_count(self.user, 3)
    
    def test_set_security_answers_insufficient_count(self):
        """Test setting insufficient security answers."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/set-security-answers/'
        data = {
            'answers': [
                {'question_id': self.security_questions[0].id, 'answer': 'Gandalf'}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('at least 2 elements', str(response.data))
    
    def test_set_security_answers_duplicate_questions(self):
        """Test setting security answers with duplicate questions."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/set-security-answers/'
        data = {
            'answers': [
                {'question_id': self.security_questions[0].id, 'answer': 'Answer1'},
                {'question_id': self.security_questions[0].id, 'answer': 'Answer2'}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('only be answered once', str(response.data))
    
    def test_set_security_answers_invalid_question(self):
        """Test setting security answers with invalid question ID."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/set-security-answers/'
        data = {
            'answers': [
                {'question_id': 99999, 'answer': 'Answer1'},
                {'question_id': self.security_questions[0].id, 'answer': 'Answer2'}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_set_security_answers_empty_answer(self):
        """Test setting security answers with empty answer."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/set-security-answers/'
        data = {
            'answers': [
                {'question_id': self.security_questions[0].id, 'answer': ''},
                {'question_id': self.security_questions[1].id, 'answer': 'Valid Answer'}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_set_security_answers_replaces_existing(self):
        """Test that setting security answers replaces existing ones."""
        self.authenticate_user(self.user)
        
        # Create initial security answers
        self.create_security_answers(self.user)
        self.assert_security_answers_count(self.user, 3)
        
        # Set new security answers
        url = '/api/auth/set-security-answers/'
        data = {
            'answers': [
                {'question_id': self.security_questions[0].id, 'answer': 'New Answer 1'},
                {'question_id': self.security_questions[1].id, 'answer': 'New Answer 2'}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['count'], 2)
        
        # Check old answers were replaced
        self.assert_security_answers_count(self.user, 2)
    
    def test_clear_security_answers(self):
        """Test clearing all security answers."""
        self.authenticate_user(self.user)
        self.create_security_answers(self.user)
        
        url = '/api/auth/clear-security-answers/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        
        # Check answers were cleared
        self.assert_security_answers_count(self.user, 0)
    
    def test_clear_security_answers_none_existing(self):
        """Test clearing security answers when none exist."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/clear-security-answers/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)


class AdminSecurityManagementAPITests(BaseTestCase):
    """
    Tests for admin security management API.
    """
    
    def test_list_security_questions_as_admin(self):
        """Test listing security questions as admin."""
        self.authenticate_user(self.admin_user)
        
        url = '/api/auth/admin/security-questions/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Admin view should include is_active field
        question = response.data['results'][0]
        self.assertIn('is_active', question)
        self.assertIn('created_at', question)
    
    def test_list_security_questions_as_regular_user(self):
        """Test listing security questions as regular user (should fail)."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/admin/security-questions/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_security_question_as_admin(self):
        """Test creating security question as admin."""
        self.authenticate_user(self.admin_user)
        
        url = '/api/auth/admin/security-questions/'
        data = {
            'question_text': 'What is your favorite spell?',
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['question_text'], 'What is your favorite spell?')
        
        # Check question was created in database
        self.assertTrue(
            SecurityQuestion.objects.filter(
                question_text='What is your favorite spell?'
            ).exists()
        )
    
    def test_create_security_question_as_regular_user(self):
        """Test creating security question as regular user (should fail)."""
        self.authenticate_user(self.user)
        
        url = '/api/auth/admin/security-questions/'
        data = {
            'question_text': 'What is your favorite spell?',
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_toggle_security_question_status(self):
        """Test toggling security question active status."""
        self.authenticate_user(self.admin_user)
        question = self.security_questions[0]
        original_status = question.is_active
        
        url = f'/api/auth/admin/security-questions/{question.id}/toggle/'
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_active'], not original_status)
        
        # Check database was updated
        question.refresh_from_db()
        self.assertEqual(question.is_active, not original_status)
    
    def test_toggle_nonexistent_security_question(self):
        """Test toggling nonexistent security question."""
        self.authenticate_user(self.admin_user)
        
        url = '/api/auth/admin/security-questions/99999/toggle/'
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_toggle_security_question_as_regular_user(self):
        """Test toggling security question as regular user (should fail)."""
        self.authenticate_user(self.user)
        question = self.security_questions[0]
        
        url = f'/api/auth/admin/security-questions/{question.id}/toggle/'
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 