"""
User Profile Serializers.
"""
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from ....models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for reading user profile information.
    """
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'full_name', 'avatar', 'is_email_verified',
            'date_joined', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'email', 'is_email_verified', 
            'date_joined', 'last_login', 'created_at', 'updated_at'
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'avatar'
        ]
        extra_kwargs = {
            'first_name': {
                'help_text': _('Your first name')
            },
            'last_name': {
                'help_text': _('Your last name')
            },
            'avatar': {
                'help_text': _('Profile picture (optional)')
            }
        }
    
    def validate_first_name(self, value):
        """
        Validate first name is not empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError(_('First name cannot be empty'))
        return value.strip()
    
    def validate_last_name(self, value):
        """
        Validate last name is not empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError(_('Last name cannot be empty'))
        return value.strip()


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users (minimal information).
    """
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'avatar', 
            'is_active', 'date_joined'
        ]
        read_only_fields = fields 