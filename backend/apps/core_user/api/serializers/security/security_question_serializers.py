"""
Security Question Serializers.
"""
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from ....models import SecurityQuestion, UserSecurityAnswer


class SecurityQuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for security questions.
    """
    class Meta:
        model = SecurityQuestion
        fields = ['id', 'question_text']
        read_only_fields = fields


class UserSecurityAnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for reading user security answers (without revealing answers).
    """
    question = SecurityQuestionSerializer(read_only=True)
    
    class Meta:
        model = UserSecurityAnswer
        fields = ['id', 'question', 'created_at', 'updated_at']
        read_only_fields = fields


class SecurityAnswerCreateSerializer(serializers.Serializer):
    """
    Serializer for creating/updating security answers.
    """
    question_id = serializers.IntegerField(
        help_text=_('ID of the security question')
    )
    answer = serializers.CharField(
        write_only=True,
        max_length=500,
        help_text=_('Your answer to the security question')
    )
    
    def validate_question_id(self, value):
        """
        Validate that the security question exists and is active.
        """
        try:
            question = SecurityQuestion.objects.get(id=value, is_active=True)
            return value
        except SecurityQuestion.DoesNotExist:
            raise serializers.ValidationError(_('Invalid security question'))
    
    def validate_answer(self, value):
        """
        Validate answer is not empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError(_('Answer cannot be empty'))
        return value.strip()


class SecurityAnswerBulkCreateSerializer(serializers.Serializer):
    """
    Serializer for creating multiple security answers at once.
    """
    answers = serializers.ListField(
        child=SecurityAnswerCreateSerializer(),
        min_length=2,
        max_length=8,
        help_text=_('List of security question answers (minimum 2)')
    )
    
    def validate_answers(self, value):
        """
        Validate that question IDs are unique.
        """
        question_ids = [answer['question_id'] for answer in value]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError(
                _('Each security question can only be answered once')
            )
        return value
    
    def create(self, validated_data):
        """
        Create multiple security answers for the user.
        """
        user = self.context['request'].user
        answers_data = validated_data['answers']
        
        # Delete existing answers
        user.security_answers.all().delete()
        
        # Create new answers
        created_answers = []
        for answer_data in answers_data:
            security_answer = UserSecurityAnswer.objects.create(
                user=user,
                question_id=answer_data['question_id']
            )
            security_answer.set_answer(answer_data['answer'])
            created_answers.append(security_answer)
        
        return created_answers


class SecurityQuestionManagementSerializer(serializers.ModelSerializer):
    """
    Serializer for managing security questions (admin only).
    """
    class Meta:
        model = SecurityQuestion
        fields = ['id', 'question_text', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'question_text': {
                'help_text': _('The security question text')
            },
            'is_active': {
                'help_text': _('Whether this question is available for users')
            }
        } 