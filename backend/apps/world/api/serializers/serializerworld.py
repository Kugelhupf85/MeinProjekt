"""
World Serializers
"""

from rest_framework import serializers
from apps.world.models import World


class WorldCreateSerializer(serializers.Serializer):
    """
    Serializer for creating worlds
    """
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=5000)
    general_mood = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    important_locations = serializers.JSONField(required=False, default=list)
    conventions = serializers.JSONField(required=False, default=dict)
    time_system = serializers.JSONField(required=False, default=dict)
    current_date = serializers.CharField(max_length=100, required=False, allow_blank=True)
    measurement_units = serializers.JSONField(required=False, default=dict)
    religions = serializers.JSONField(required=False, default=list)
    magic_system = serializers.JSONField(required=False, default=dict)
    political_systems = serializers.JSONField(required=False, default=list)
    languages = serializers.JSONField(required=False, default=list)
    history_timeline = serializers.JSONField(required=False, default=list)
    climate_zones = serializers.JSONField(required=False, default=list)
    natural_phenomena = serializers.JSONField(required=False, default=list)
    trade_routes = serializers.JSONField(required=False, default=list)
    conflicts_tensions = serializers.JSONField(required=False, default=list)
    is_active = serializers.BooleanField(required=False, default=True)


class WorldUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating worlds
    """
    name = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(max_length=5000, required=False)
    general_mood = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    important_locations = serializers.JSONField(required=False)
    conventions = serializers.JSONField(required=False)
    time_system = serializers.JSONField(required=False)
    current_date = serializers.CharField(max_length=100, required=False, allow_blank=True)
    measurement_units = serializers.JSONField(required=False)
    religions = serializers.JSONField(required=False)
    magic_system = serializers.JSONField(required=False)
    political_systems = serializers.JSONField(required=False)
    languages = serializers.JSONField(required=False)
    history_timeline = serializers.JSONField(required=False)
    climate_zones = serializers.JSONField(required=False)
    natural_phenomena = serializers.JSONField(required=False)
    trade_routes = serializers.JSONField(required=False)
    conflicts_tensions = serializers.JSONField(required=False)
    is_active = serializers.BooleanField(required=False)


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


class WorldListSerializer(serializers.ModelSerializer):
    """
    Serializer for world list responses
    """
    region_count = serializers.ReadOnlyField()
    total_locations = serializers.ReadOnlyField()
    
    class Meta:
        model = World
        fields = [
            'entity_id', 'name', 'description', 'general_mood',
            'region_count', 'total_locations', 'created_at', 'updated_at'
        ]


class WorldStatisticsSerializer(serializers.Serializer):
    """
    Serializer for world statistics
    """
    entity_id = serializers.CharField()
    name = serializers.CharField()
    region_count = serializers.IntegerField()
    total_locations = serializers.IntegerField()
    active_adventures = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField() 