"""
Password Management Serializers.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from ....models import User, UserSecurityAnswer


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing password (requires current password).
    """
    current_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text=_('Your current password')
    )
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text=_('Your new password')
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text=_('Confirm your new password')
    )
    
    def validate_current_password(self, value):
        """
        Validate current password.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_('Current password is incorrect'))
        return value
    
    def validate(self, attrs):
        """
        Validate that new passwords match.
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': _("New passwords don't match")
            })
        return attrs
    
    def save(self):
        """
        Update user password.
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset via email.
    """
    email = serializers.EmailField(
        help_text=_('Email address of the account')
    )
    
    def validate_email(self, value):
        """
        Validate that email exists.
        """
        try:
            user = User.objects.get(email=value, is_active=True)
            self.context['user'] = user
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            pass
        return value


class PasswordResetWithSecuritySerializer(serializers.Serializer):
    """
    Serializer for password reset using security questions.
    """
    email = serializers.EmailField(
        help_text=_('Email address of the account')
    )
    security_answers = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        min_length=2,
        help_text=_('List of security question answers')
    )
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text=_('Your new password')
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text=_('Confirm your new password')
    )
    
    def validate_email(self, value):
        """
        Validate that email exists and has security answers.
        """
        try:
            user = User.objects.get(email=value, is_active=True)
            if user.security_answers.count() < 2:
                raise serializers.ValidationError(
                    _('This account does not have enough security questions set up')
                )
            self.context['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError(_('Account not found'))
        return value
    
    def validate_security_answers(self, value):
        """
        Validate security answers.
        """
        user = self.context.get('user')
        if not user:
            return value
        
        # Convert list of dicts to dict with question_id as key
        answers_dict = {}
        for answer_item in value:
            question_id = answer_item.get('question_id')
            answer = answer_item.get('answer')
            if question_id and answer:
                answers_dict[int(question_id)] = answer
        
        if len(answers_dict) < 2:
            raise serializers.ValidationError(
                _('At least 2 security answers are required')
            )
        
        # Validate answers
        if not UserSecurityAnswer.validate_user_answers(user, answers_dict):
            raise serializers.ValidationError(
                _('One or more security answers are incorrect')
            )
        
        return value
    
    def validate(self, attrs):
        """
        Validate that new passwords match.
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': _("New passwords don't match")
            })
        return attrs
    
    def save(self):
        """
        Update user password after security validation.
        """
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user 