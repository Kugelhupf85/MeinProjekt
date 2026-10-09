"""
Registration Serializers for User Creation.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from ....models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with email verification.
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text=_('Password for the new account')
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text=_('Confirm your password')
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 
            'password', 'password_confirm'
        ]
        extra_kwargs = {
            'email': {
                'help_text': _('Email address (will be used for login)')
            },
            'first_name': {
                'help_text': _('Your first name')
            },
            'last_name': {
                'help_text': _('Your last name')
            }
        }
    
    def validate(self, attrs):
        """
        Validate that passwords match and email is unique.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': _("Passwords don't match")
            })
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                'email': _('A user with this email already exists.')
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Create user with email verification token.
        """
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        user.generate_email_verification_token()
        return user


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification.
    """
    token = serializers.CharField(
        help_text=_('Email verification token')
    )
    
    def validate_token(self, value):
        """
        Validate the verification token.
        """
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError(_('User context required'))
        
        if not user.verify_email(value):
            raise serializers.ValidationError(_('Invalid verification token'))
        return value 