"""
Serializers for UserKeys model API.
"""
from rest_framework import serializers
from ...models import UserKeys


class UserKeysOutputSerializer(serializers.ModelSerializer):
    """
    Serializer for UserKeys output (GET requests).
    """
    configured_providers = serializers.SerializerMethodField()
    
    class Meta:
        model = UserKeys
        fields = [
            'id',
            'dungeonmaster',
            'openai_status',
            'anthropic_status',
            'google_status',
            'deepseek_status',
            'openai_last_validated',
            'anthropic_last_validated',
            'google_last_validated',
            'deepseek_last_validated',
            'usage_statistics',
            'encryption_version',
            'last_key_update',
            'security_notes',
            'configured_providers',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'configured_providers',
            'last_key_update', 'encryption_version'
        ]
    
    def get_configured_providers(self, obj):
        """Get list of configured providers."""
        return obj.get_configured_providers()


class UserKeysCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating UserKeys (POST requests).
    """
    class Meta:
        model = UserKeys
        fields = [
            'dungeonmaster',
            'security_notes'
        ]


class UserKeysUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating UserKeys (PUT/PATCH requests).
    """
    class Meta:
        model = UserKeys
        fields = [
            'security_notes'
        ]


class APIKeyUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating API keys.
    """
    provider = serializers.ChoiceField(
        choices=['openai', 'anthropic', 'google', 'deepseek']
    )
    api_key = serializers.CharField(
        max_length=500,
        write_only=True,
        help_text="API key to store (will be encrypted)"
    )


class APIKeySetSerializer(serializers.Serializer):
    """
    Serializer for setting API keys.
    """
    provider = serializers.ChoiceField(
        choices=['openai', 'anthropic', 'google', 'deepseek']
    )
    api_key = serializers.CharField(
        max_length=500,
        write_only=True,
        help_text="API key to store (will be encrypted)"
    )


class APIKeyDeleteSerializer(serializers.Serializer):
    """
    Serializer for deleting API keys.
    """
    provider = serializers.ChoiceField(
        choices=['openai', 'anthropic', 'google', 'deepseek']
    )


class APIKeyStatusSerializer(serializers.Serializer):
    """
    Serializer for API key status information.
    """
    provider = serializers.CharField(max_length=20)
    status = serializers.CharField(max_length=20)
    last_validated = serializers.DateTimeField(allow_null=True)
    usage_today = serializers.IntegerField()


class UsageStatsSerializer(serializers.Serializer):
    """
    Serializer for usage statistics.
    """
    provider = serializers.CharField(max_length=20)
    requests_today = serializers.IntegerField()
    last_request = serializers.DateTimeField(allow_null=True)


class UsageIncrementSerializer(serializers.Serializer):
    """
    Serializer for incrementing usage.
    """
    provider = serializers.ChoiceField(
        choices=['openai', 'anthropic', 'google', 'deepseek']
    )


class UserKeysStatusSerializer(serializers.Serializer):
    """
    Serializer for overall UserKeys status.
    """
    total_configured = serializers.IntegerField()
    configured_providers = serializers.ListField(
        child=serializers.CharField(max_length=20)
    )
    last_update = serializers.DateTimeField()


class UserKeysCompactSerializer(serializers.ModelSerializer):
    """
    Compact serializer for UserKeys.
    """
    class Meta:
        model = UserKeys
        fields = [
            'id',
            'dungeonmaster',
            'openai_status',
            'anthropic_status',
            'google_status',
            'deepseek_status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 