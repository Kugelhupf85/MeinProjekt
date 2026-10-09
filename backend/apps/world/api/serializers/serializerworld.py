"""
World Serializers
"""

from rest_framework import serializers
from apps.world.models import World, WorldAPIKeys, WorldParty, WorldPartyMembership
from django.contrib.auth import get_user_model

User = get_user_model()


class WorldCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating worlds."""
    
    class Meta:
        model = World
        fields = [
            'name', 'description', 'general_mood', 'important_locations',
            'conventions', 'time_system', 'current_date', 'measurement_units',
            'religions', 'magic_system', 'political_systems', 'languages',
            'history_timeline', 'climate_zones', 'natural_phenomena',
            'trade_routes', 'conflicts_tensions'
        ]
    
    def validate_name(self, value):
        """Validate world name uniqueness."""
        if World.objects.filter(name=value, is_active=True).exists():
            raise serializers.ValidationError("A world with this name already exists.")
        return value


class WorldUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating worlds."""
    
    class Meta:
        model = World
        fields = [
            'name', 'description', 'general_mood', 'important_locations',
            'conventions', 'time_system', 'current_date', 'measurement_units',
            'religions', 'magic_system', 'political_systems', 'languages',
            'history_timeline', 'climate_zones', 'natural_phenomena',
            'trade_routes', 'conflicts_tensions'
        ]
    
    def validate_name(self, value):
        """Validate world name uniqueness."""
        if World.objects.filter(name=value, is_active=True).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("A world with this name already exists.")
        return value


class WorldDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for world detail responses
    """
    region_count = serializers.ReadOnlyField()
    total_locations = serializers.ReadOnlyField()
    
    class Meta:
        model = World
        fields = [
            'entity_id', 'name', 'description', 'general_mood',
            'important_locations', 'conventions', 'time_system', 'current_date',
            'measurement_units', 'religions', 'magic_system', 'political_systems',
            'languages', 'history_timeline', 'climate_zones', 'natural_phenomena',
            'trade_routes', 'conflicts_tensions', 'region_count', 'total_locations',
            'created_at', 'updated_at', 'is_active'
        ]


class WorldAPIKeysSerializer(serializers.ModelSerializer):
    """
    Serializer for World API Keys
    """
    world_name = serializers.CharField(source='world.name', read_only=True)
    configured_providers = serializers.SerializerMethodField()
    
    class Meta:
        model = WorldAPIKeys
        fields = [
            'id', 'world', 'world_name', 'openai_status', 'anthropic_status',
            'google_status', 'deepseek_status', 'openai_last_validated',
            'anthropic_last_validated', 'google_last_validated',
            'deepseek_last_validated', 'usage_statistics', 'encryption_version',
            'last_key_update', 'security_notes', 'configured_providers',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'world', 'world_name', 'openai_last_validated',
            'anthropic_last_validated', 'google_last_validated',
            'deepseek_last_validated', 'usage_statistics', 'encryption_version',
            'last_key_update', 'created_at', 'updated_at'
        ]
    
    def get_configured_providers(self, obj):
        """Get list of configured API providers."""
        return obj.get_configured_providers()


class WorldAPIKeyUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating API key status
    """
    provider = serializers.ChoiceField(choices=['openai', 'anthropic', 'google', 'deepseek'])
    status = serializers.ChoiceField(choices=WorldAPIKeys.KEY_STATUS_CHOICES)
    security_notes = serializers.CharField(required=False, allow_blank=True)


class WorldPartySerializer(serializers.ModelSerializer):
    """
    Serializer for World Party
    """
    world_name = serializers.CharField(source='world.name', read_only=True)
    creator_email = serializers.CharField(source='creator.email', read_only=True)
    member_count = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    
    class Meta:
        model = WorldParty
        fields = [
            'entity_id', 'world', 'world_name', 'name', 'description',
            'creator', 'creator_email', 'is_active', 'is_public', 'max_members',
            'party_settings', 'member_count', 'is_full', 'created_at', 'updated_at'
        ]
        read_only_fields = ['entity_id', 'world', 'creator', 'creator_email', 'created_at', 'updated_at']


class WorldPartyMembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for World Party Membership
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_display_name = serializers.CharField(source='user.display_name', read_only=True)
    party_name = serializers.CharField(source='party.name', read_only=True)
    
    class Meta:
        model = WorldPartyMembership
        fields = [
            'id', 'user', 'user_email', 'user_display_name', 'party', 'party_name',
            'role', 'status', 'can_invite_members', 'can_manage_campaigns',
            'can_edit_party', 'can_change_roles', 'can_remove_members',
            'can_access_api_keys', 'joined_at', 'last_active'
        ]
        read_only_fields = [
            'id', 'user_email', 'user_display_name', 'party_name',
            'can_invite_members', 'can_manage_campaigns', 'can_edit_party',
            'can_change_roles', 'can_remove_members', 'can_access_api_keys',
            'joined_at', 'last_active'
        ]


class WorldPartyMembershipUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating party membership
    """
    role = serializers.ChoiceField(choices=WorldPartyMembership.ROLE_CHOICES, required=False)
    status = serializers.ChoiceField(choices=WorldPartyMembership.STATUS_CHOICES, required=False)


class WorldPartyInviteSerializer(serializers.Serializer):
    """
    Serializer for inviting users to a party
    """
    user_email = serializers.EmailField()
    role = serializers.ChoiceField(choices=WorldPartyMembership.ROLE_CHOICES, default='player') 