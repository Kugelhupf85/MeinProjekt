"""
Location Serializers
"""

from rest_framework import serializers
from apps.world.models import Location


class LocationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new location."""
    
    class Meta:
        model = Location
        fields = [
            'name', 'location_type', 'description', 'general_mood', 'size_scale',
            'accessibility', 'important_personalities', 'services_available',
            'notable_features', 'secrets_hidden', 'encounters_possible',
            'items_treasures', 'defenses_security', 'population_demographics',
            'economic_activity', 'connections_travel', 'rumors_information',
            'seasonal_changes', 'current_events', 'quest_opportunities'
        ]
    
    def validate_name(self, value):
        """Validate location name uniqueness within region."""
        region = self.context.get('region')
        if region and Location.objects.filter(region=region, name=value, is_active=True).exists():
            raise serializers.ValidationError("A location with this name already exists in this region.")
        return value


class LocationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a location."""
    
    class Meta:
        model = Location
        fields = [
            'name', 'location_type', 'description', 'general_mood', 'size_scale',
            'accessibility', 'important_personalities', 'services_available',
            'notable_features', 'secrets_hidden', 'encounters_possible',
            'items_treasures', 'defenses_security', 'population_demographics',
            'economic_activity', 'connections_travel', 'rumors_information',
            'seasonal_changes', 'current_events', 'quest_opportunities'
        ]
    
    def validate_name(self, value):
        """Validate location name uniqueness within region."""
        region = self.context.get('region')
        if region and Location.objects.filter(region=region, name=value, is_active=True).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("A location with this name already exists in this region.")
        return value


class LocationListSerializer(serializers.ModelSerializer):
    """Serializer for listing locations with basic information."""
    
    region_name = serializers.CharField(source='region.name', read_only=True)
    region_entity_id = serializers.CharField(source='region.entity_id', read_only=True)
    world_name = serializers.CharField(source='world.name', read_only=True)
    world_entity_id = serializers.CharField(source='world.entity_id', read_only=True)
    location_type_display = serializers.CharField(source='get_location_type_display', read_only=True)
    
    class Meta:
        model = Location
        fields = [
            'id', 'entity_id', 'name', 'location_type', 'location_type_display',
            'description', 'general_mood', 'size_scale', 'accessibility',
            'region_name', 'region_entity_id', 'world_name', 'world_entity_id',
            'created_at', 'updated_at'
        ]


class LocationDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed location information."""
    
    region_name = serializers.CharField(source='region.name', read_only=True)
    region_entity_id = serializers.CharField(source='region.entity_id', read_only=True)
    world_name = serializers.CharField(source='world.name', read_only=True)
    world_entity_id = serializers.CharField(source='world.entity_id', read_only=True)
    location_type_display = serializers.CharField(source='get_location_type_display', read_only=True)
    full_path = serializers.CharField(read_only=True)
    key_npcs = serializers.SerializerMethodField()
    available_services = serializers.SerializerMethodField()
    current_plot_hooks = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = [
            'id', 'entity_id', 'name', 'location_type', 'location_type_display',
            'description', 'general_mood', 'size_scale', 'accessibility',
            'region_name', 'region_entity_id', 'world_name', 'world_entity_id',
            'full_path', 'important_personalities', 'services_available',
            'notable_features', 'secrets_hidden', 'encounters_possible',
            'items_treasures', 'defenses_security', 'population_demographics',
            'economic_activity', 'connections_travel', 'rumors_information',
            'seasonal_changes', 'current_events', 'quest_opportunities',
            'key_npcs', 'available_services', 'current_plot_hooks',
            'created_at', 'updated_at'
        ]
    
    def get_key_npcs(self, obj):
        """Get list of key NPCs with high importance."""
        return obj.get_key_npcs()
    
    def get_available_services(self, obj):
        """Get list of available services for quick reference."""
        return obj.get_available_services()
    
    def get_current_plot_hooks(self, obj):
        """Get current active plot hooks and quest opportunities."""
        return obj.get_current_plot_hooks() 