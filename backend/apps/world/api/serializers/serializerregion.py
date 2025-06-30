"""
Region Serializers
"""

from rest_framework import serializers
from apps.world.models import Region


class RegionCreateSerializer(serializers.Serializer):
    """
    Serializer for creating regions
    """
    world_id = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=3000)
    general_mood = serializers.CharField(max_length=800, required=False, allow_blank=True)
    currencies = serializers.JSONField(required=False, default=list)
    important_personalities = serializers.JSONField(required=False, default=list)
    religions = serializers.JSONField(required=False, default=list)
    government_type = serializers.JSONField(required=False, default=dict)
    cultural_traits = serializers.JSONField(required=False, default=list)
    major_settlements = serializers.JSONField(required=False, default=list)
    natural_resources = serializers.JSONField(required=False, default=list)
    trade_specialties = serializers.JSONField(required=False, default=list)
    threats_dangers = serializers.JSONField(required=False, default=list)
    climate_weather = serializers.JSONField(required=False, default=dict)
    laws_customs = serializers.JSONField(required=False, default=list)
    festivals_events = serializers.JSONField(required=False, default=list)
    military_forces = serializers.JSONField(required=False, default=dict)
    terrain_type = serializers.CharField(max_length=100, required=False, allow_blank=True)
    size_description = serializers.CharField(max_length=200, required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False, default=True)


class RegionUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating regions
    """
    name = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(max_length=3000, required=False)
    general_mood = serializers.CharField(max_length=800, required=False, allow_blank=True)
    currencies = serializers.JSONField(required=False)
    important_personalities = serializers.JSONField(required=False)
    religions = serializers.JSONField(required=False)
    government_type = serializers.JSONField(required=False)
    cultural_traits = serializers.JSONField(required=False)
    major_settlements = serializers.JSONField(required=False)
    natural_resources = serializers.JSONField(required=False)
    trade_specialties = serializers.JSONField(required=False)
    threats_dangers = serializers.JSONField(required=False)
    climate_weather = serializers.JSONField(required=False)
    laws_customs = serializers.JSONField(required=False)
    festivals_events = serializers.JSONField(required=False)
    military_forces = serializers.JSONField(required=False)
    terrain_type = serializers.CharField(max_length=100, required=False, allow_blank=True)
    size_description = serializers.CharField(max_length=200, required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)


class RegionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for region detail responses
    """
    world_name = serializers.CharField(source='world.name', read_only=True)
    world_id = serializers.CharField(source='world.entity_id', read_only=True)
    location_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Region
        fields = [
            'entity_id', 'world_id', 'world_name', 'name', 'description', 'general_mood',
            'currencies', 'important_personalities', 'religions', 'government_type',
            'cultural_traits', 'major_settlements', 'natural_resources', 'trade_specialties',
            'threats_dangers', 'climate_weather', 'laws_customs', 'festivals_events',
            'military_forces', 'terrain_type', 'size_description', 'location_count',
            'created_at', 'updated_at', 'is_active'
        ]


class RegionListSerializer(serializers.ModelSerializer):
    """
    Serializer for region list responses
    """
    world_name = serializers.CharField(source='world.name', read_only=True)
    world_id = serializers.CharField(source='world.entity_id', read_only=True)
    location_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Region
        fields = [
            'entity_id', 'world_id', 'world_name', 'name', 'description', 'general_mood',
            'terrain_type', 'location_count', 'created_at', 'updated_at'
        ]


class RegionStatisticsSerializer(serializers.Serializer):
    """
    Serializer for region statistics
    """
    entity_id = serializers.CharField()
    name = serializers.CharField()
    world_name = serializers.CharField()
    world_id = serializers.CharField()
    location_count = serializers.IntegerField()
    major_personalities_count = serializers.IntegerField()
    primary_currency = serializers.JSONField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField() 