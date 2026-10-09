"""
Security Questions System for Password Reset.
"""
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class SecurityQuestion(models.Model):
    """
    Predefined security questions for password reset.
    """
    
    question_text = models.CharField(
        max_length=500,
        unique=True,
        help_text=_('The security question text')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this question is available for selection')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Timestamp when the question was created')
    )
    
    class Meta:
        db_table = 'core_security_question'
        verbose_name = _('Security Question')
        verbose_name_plural = _('Security Questions')
        ordering = ['question_text']
    
    def __str__(self):
        return self.question_text


class UserSecurityAnswer(models.Model):
    """
    User's answers to security questions with hashed storage.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='security_answers',
        help_text=_('The user who provided this answer')
    )
    
    question = models.ForeignKey(
        SecurityQuestion,
        on_delete=models.CASCADE,
        help_text=_('The security question')
    )
    
    answer_hash = models.CharField(
        max_length=128,
        help_text=_('Hashed answer to the security question')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Timestamp when the answer was created')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('Timestamp when the answer was last updated')
    )
    
    class Meta:
        db_table = 'core_user_security_answer'
        verbose_name = _('User Security Answer')
        verbose_name_plural = _('User Security Answers')
        unique_together = ['user', 'question']
        ordering = ['user', 'question']
    
    def __str__(self):
        return f"{self.user.email} - {self.question.question_text}"
    
    def set_answer(self, raw_answer):
        """
        Set the answer with proper hashing.
        """
        # Convert to lowercase and strip whitespace for consistency
        normalized_answer = raw_answer.lower().strip()
        self.answer_hash = make_password(normalized_answer)
        self.save(update_fields=['answer_hash', 'updated_at'])
    
    def check_answer(self, raw_answer):
        """
        Check if the provided answer matches the stored hash.
        """
        # Convert to lowercase and strip whitespace for consistency
        normalized_answer = raw_answer.lower().strip()
        return check_password(normalized_answer, self.answer_hash)
    
    @classmethod
    def validate_user_answers(cls, user, answers_dict):
        """
        Validate multiple security answers for a user.
        
        Args:
            user: The user instance
            answers_dict: Dict with question_id as key and answer as value
        
        Returns:
            bool: True if all answers are correct
        """
        user_answers = cls.objects.filter(
            user=user,
            question_id__in=answers_dict.keys()
        )
        
        if len(user_answers) != len(answers_dict):
            return False
        
        for user_answer in user_answers:
            provided_answer = answers_dict.get(user_answer.question_id)
            if not user_answer.check_answer(provided_answer):
                return False
        
        return True 