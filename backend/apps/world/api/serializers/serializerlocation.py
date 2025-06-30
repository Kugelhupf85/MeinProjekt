"""
Location Serializers
"""

from rest_framework import serializers
from apps.world.models import Location


class LocationCreateSerializer(serializers.Serializer):
    """
    Serializer for creating locations
    """
    region_id = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=200)
    location_type = serializers.ChoiceField(choices=Location.LOCATION_TYPES, default='other')
    description = serializers.CharField(max_length=2000)
    general_mood = serializers.CharField(max_length=600, required=False, allow_blank=True)
    important_personalities = serializers.JSONField(required=False, default=list)
    services_available = serializers.JSONField(required=False, default=list)
    notable_features = serializers.JSONField(required=False, default=list)
    secrets_hidden = serializers.JSONField(required=False, default=list)
    encounters_possible = serializers.JSONField(required=False, default=list)
    items_treasures = serializers.JSONField(required=False, default=list)
    defenses_security = serializers.JSONField(required=False, default=dict)
    population_demographics = serializers.JSONField(required=False, default=dict)
    economic_activity = serializers.JSONField(required=False, default=list)
    connections_travel = serializers.JSONField(required=False, default=list)
    rumors_information = serializers.JSONField(required=False, default=list)
    seasonal_changes = serializers.JSONField(required=False, default=dict)
    size_scale = serializers.CharField(max_length=50, required=False, allow_blank=True)
    accessibility = serializers.CharField(max_length=100, required=False, allow_blank=True)
    current_events = serializers.JSONField(required=False, default=list)
    quest_opportunities = serializers.JSONField(required=False, default=list)
    is_active = serializers.BooleanField(required=False, default=True)


class LocationUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating locations
    """
    name = serializers.CharField(max_length=200, required=False)
    location_type = serializers.ChoiceField(choices=Location.LOCATION_TYPES, required=False)
    description = serializers.CharField(max_length=2000, required=False)
    general_mood = serializers.CharField(max_length=600, required=False, allow_blank=True)
    important_personalities = serializers.JSONField(required=False)
    services_available = serializers.JSONField(required=False)
    notable_features = serializers.JSONField(required=False)
    secrets_hidden = serializers.JSONField(required=False)
    encounters_possible = serializers.JSONField(required=False)
    items_treasures = serializers.JSONField(required=False)
    defenses_security = serializers.JSONField(required=False)
    population_demographics = serializers.JSONField(required=False)
    economic_activity = serializers.JSONField(required=False)
    connections_travel = serializers.JSONField(required=False)
    rumors_information = serializers.JSONField(required=False)
    seasonal_changes = serializers.JSONField(required=False)
    size_scale = serializers.CharField(max_length=50, required=False, allow_blank=True)
    accessibility = serializers.CharField(max_length=100, required=False, allow_blank=True)
    current_events = serializers.JSONField(required=False)
    quest_opportunities = serializers.JSONField(required=False)
    is_active = serializers.BooleanField(required=False)


class LocationDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for location detail responses
    """
    region_name = serializers.CharField(source='region.name', read_only=True)
    region_id = serializers.CharField(source='region.entity_id', read_only=True)
    world_name = serializers.CharField(source='region.world.name', read_only=True)
    world_id = serializers.CharField(source='region.world.entity_id', read_only=True)
    full_path = serializers.ReadOnlyField()
    
    class Meta:
        model = Location
        fields = [
            'entity_id', 'region_id', 'region_name', 'world_id', 'world_name',
            'name', 'location_type', 'description', 'general_mood', 'full_path',
            'important_personalities', 'services_available', 'notable_features',
            'secrets_hidden', 'encounters_possible', 'items_treasures',
            'defenses_security', 'population_demographics', 'economic_activity',
            'connections_travel', 'rumors_information', 'seasonal_changes',
            'size_scale', 'accessibility', 'current_events', 'quest_opportunities',
            'created_at', 'updated_at', 'is_active'
        ]


class LocationListSerializer(serializers.ModelSerializer):
    """
    Serializer for location list responses
    """
    region_name = serializers.CharField(source='region.name', read_only=True)
    region_id = serializers.CharField(source='region.entity_id', read_only=True)
    world_name = serializers.CharField(source='region.world.name', read_only=True)
    world_id = serializers.CharField(source='region.world.entity_id', read_only=True)
    full_path = serializers.ReadOnlyField()
    
    class Meta:
        model = Location
        fields = [
            'entity_id', 'region_id', 'region_name', 'world_id', 'world_name',
            'name', 'location_type', 'description', 'general_mood', 'full_path',
            'size_scale', 'accessibility', 'created_at', 'updated_at'
        ]


class LocationStatisticsSerializer(serializers.Serializer):
    """
    Serializer for location statistics
    """
    entity_id = serializers.CharField()
    name = serializers.CharField()
    location_type = serializers.CharField()
    region_name = serializers.CharField()
    region_id = serializers.CharField()
    world_name = serializers.CharField()
    world_id = serializers.CharField()
    full_path = serializers.CharField()
    key_npcs_count = serializers.IntegerField()
    available_services_count = serializers.IntegerField()
    plot_hooks_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField() 