"""
Serializers for UserSettings model API.
"""
from rest_framework import serializers
from ...models import UserSettings


class UserSettingsOutputSerializer(serializers.ModelSerializer):
    """
    Serializer for UserSettings output (GET requests).
    """
    class Meta:
        model = UserSettings
        fields = [
            'id',
            'dungeonmaster',
            'ui_settings',
            'ai_settings',
            'feature_flags',
            'privacy_settings',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSettingsCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating UserSettings (POST requests).
    """
    class Meta:
        model = UserSettings
        fields = [
            'dungeonmaster',
            'ui_settings',
            'ai_settings',
            'feature_flags',
            'privacy_settings'
        ]


class UserSettingsUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating UserSettings (PUT/PATCH requests).
    """
    class Meta:
        model = UserSettings
        fields = [
            'ui_settings',
            'ai_settings',
            'feature_flags',
            'privacy_settings'
        ]


class UISettingUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating UI settings.
    """
    key = serializers.CharField(max_length=100)
    value = serializers.JSONField()


class AISettingUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating AI settings.
    """
    key = serializers.CharField(max_length=100)
    value = serializers.JSONField()


class FeatureFlagUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating feature flags.
    """
    key = serializers.CharField(max_length=100)
    value = serializers.BooleanField()


class PrivacySettingUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating privacy settings.
    """
    key = serializers.CharField(max_length=100)
    value = serializers.JSONField()


class UserSettingsCompactSerializer(serializers.ModelSerializer):
    """
    Compact serializer for UserSettings.
    """
    class Meta:
        model = UserSettings
        fields = [
            'id',
            'dungeonmaster',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 