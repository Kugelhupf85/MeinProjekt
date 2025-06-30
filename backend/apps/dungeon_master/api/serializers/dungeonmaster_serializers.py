"""
Serializers for DungeonMaster model API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from ...models import DungeonMaster


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic User information serializer for output.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'is_active']
        read_only_fields = ['id', 'username', 'date_joined']


class DungeonMasterOutputSerializer(serializers.ModelSerializer):
    """
    Serializer for DungeonMaster output (GET requests).
    Includes related User information.
    """
    user = UserBasicSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    
    class Meta:
        model = DungeonMaster
        fields = [
            'id',
            'entity_id',
            'user',
            'full_name',
            'email',
            'display_name',
            'bio',
            'experience_level',
            'strictness_level',
            'green_flags',
            'red_flags',
            'content_rating',
            'themes_preferences',
            'is_active',
            'is_public',
            'last_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'entity_id', 'created_at', 'updated_at', 'last_active']


class DungeonMasterCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new DungeonMaster (POST requests).
    """
    username = serializers.CharField(
        max_length=150,
        help_text="Unique username for the user"
    )
    email = serializers.EmailField(
        help_text="Email address for the user"
    )
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        help_text="Password for the user (minimum 8 characters)"
    )
    first_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        help_text="Optional first name"
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        help_text="Optional last name"
    )
    
    # DungeonMaster specific fields
    display_name = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text="Display name for the dungeon master"
    )
    bio = serializers.CharField(
        max_length=2000,
        required=False,
        allow_blank=True,
        help_text="Biography or description"
    )
    experience_level = serializers.ChoiceField(
        choices=DungeonMaster.EXPERIENCE_CHOICES,
        default='beginner',
        help_text="Experience level as a dungeon master"
    )
    strictness_level = serializers.IntegerField(
        min_value=1,
        max_value=10,
        default=5,
        help_text="Strictness level from 1 to 10"
    )
    green_flags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list,
        help_text="Array of positive preferences/styles"
    )
    red_flags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list,
        help_text="Array of things to avoid/dislikes"
    )
    content_rating = serializers.ChoiceField(
        choices=DungeonMaster.CONTENT_RATING_CHOICES,
        default='teen',
        help_text="Preferred content rating"
    )
    themes_preferences = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list,
        help_text="Preferred themes and genres"
    )
    is_public = serializers.BooleanField(
        default=False,
        help_text="Whether profile is publicly visible"
    )
    
    def validate_username(self, value):
        """
        Validate that username is unique.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_email(self, value):
        """
        Validate that email is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class DungeonMasterUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating DungeonMaster profile (PUT/PATCH requests).
    """
    display_name = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text="Display name for the dungeon master"
    )
    bio = serializers.CharField(
        max_length=2000,
        required=False,
        allow_blank=True,
        help_text="Biography or description"
    )
    experience_level = serializers.ChoiceField(
        choices=DungeonMaster.EXPERIENCE_CHOICES,
        required=False,
        help_text="Experience level as a dungeon master"
    )
    strictness_level = serializers.IntegerField(
        min_value=1,
        max_value=10,
        required=False,
        help_text="Strictness level from 1 to 10"
    )
    green_flags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        help_text="Array of positive preferences/styles"
    )
    red_flags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        help_text="Array of things to avoid/dislikes"
    )
    content_rating = serializers.ChoiceField(
        choices=DungeonMaster.CONTENT_RATING_CHOICES,
        required=False,
        help_text="Preferred content rating"
    )
    themes_preferences = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        help_text="Preferred themes and genres"
    )
    is_public = serializers.BooleanField(
        required=False,
        help_text="Whether profile is publicly visible"
    )


class UserUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating User information (PUT/PATCH requests).
    """
    first_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        help_text="First name"
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        help_text="Last name"
    )
    email = serializers.EmailField(
        required=False,
        help_text="Email address"
    )
    
    def validate_email(self, value):
        """
        Validate that email is unique (excluding current user).
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            current_user_id = request.user.id
            if User.objects.filter(email=value).exclude(id=current_user_id).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        return value


class DungeonMasterListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing DungeonMasters.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = DungeonMaster
        fields = [
            'id',
            'entity_id',
            'user_username',
            'user_email',
            'full_name',
            'display_name',
            'experience_level',
            'content_rating',
            'is_public',
            'created_at',
            'is_active'
        ]
        read_only_fields = ['id', 'entity_id', 'created_at']


class DungeonMasterPublicSerializer(serializers.ModelSerializer):
    """
    Public serializer for DungeonMaster profiles (limited information).
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = DungeonMaster
        fields = [
            'entity_id',
            'full_name',
            'display_name',
            'bio',
            'experience_level',
            'content_rating',
            'themes_preferences',
            'created_at'
        ]
        read_only_fields = ['entity_id', 'created_at'] 