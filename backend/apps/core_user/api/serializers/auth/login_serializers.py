"""
Login Serializers for Authentication.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from ....models import User


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login with email/username and password.
    """
    username = serializers.CharField(
        help_text=_('Email or username for login')
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        help_text=_('User password')
    )
    
    def validate(self, attrs):
        """
        Validate login credentials and authenticate user.
        """
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Try to find user by email first, then by username (if exists)
            user = None
            
            # Check if input is email format
            if '@' in username:
                try:
                    user = User.objects.get(email=username)
                except User.DoesNotExist:
                    pass
            else:
                # Fallback: try to find by username field (if it exists)
                try:
                    user = User.objects.get(username=username)
                except (User.DoesNotExist, AttributeError):
                    # Username field doesn't exist in our model
                    pass
            
            if user and user.check_password(password):
                if not user.is_active:
                    raise serializers.ValidationError(
                        _('User account is disabled.')
                    )
                
                if not user.is_email_verified:
                    raise serializers.ValidationError(
                        _('Please verify your email address before logging in.')
                    )
                
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError(
                    _('Unable to log in with provided credentials.')
                )
        else:
            raise serializers.ValidationError(
                _('Must include "username" and "password".')
            )


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for user logout.
    """
    pass  # No fields needed for logout 