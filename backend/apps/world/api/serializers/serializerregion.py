"""
Region Serializers
"""

from rest_framework import serializers
from apps.world.models import Region


class RegionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new region."""
    
    class Meta:
        model = Region
        fields = [
            'name', 'description', 'general_mood', 'terrain_type', 'size_description',
            'currencies', 'important_personalities', 'religions', 'government_type',
            'cultural_traits', 'major_settlements', 'natural_resources', 'trade_specialties',
            'threats_dangers', 'climate_weather', 'laws_customs', 'festivals_events',
            'military_forces'
        ]
    
    def validate_name(self, value):
        """Validate region name uniqueness within world."""
        world = self.context.get('world')
        if world and Region.objects.filter(world=world, name=value, is_active=True).exists():
            raise serializers.ValidationError("A region with this name already exists in this world.")
        return value


class RegionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a region."""
    
    class Meta:
        model = Region
        fields = [
            'name', 'description', 'general_mood', 'terrain_type', 'size_description',
            'currencies', 'important_personalities', 'religions', 'government_type',
            'cultural_traits', 'major_settlements', 'natural_resources', 'trade_specialties',
            'threats_dangers', 'climate_weather', 'laws_customs', 'festivals_events',
            'military_forces'
        ]
    
    def validate_name(self, value):
        """Validate region name uniqueness within world."""
        world = self.context.get('world')
        if world and Region.objects.filter(world=world, name=value, is_active=True).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("A region with this name already exists in this world.")
        return value


class RegionListSerializer(serializers.ModelSerializer):
    """Serializer for listing regions with basic information."""
    
    world_name = serializers.CharField(source='world.name', read_only=True)
    world_entity_id = serializers.CharField(source='world.entity_id', read_only=True)
    location_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Region
        fields = [
            'id', 'entity_id', 'name', 'description', 'general_mood', 'terrain_type',
            'world_name', 'world_entity_id', 'location_count', 'created_at', 'updated_at'
        ]


class RegionDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed region information."""
    
    world_name = serializers.CharField(source='world.name', read_only=True)
    world_entity_id = serializers.CharField(source='world.entity_id', read_only=True)
    location_count = serializers.IntegerField(read_only=True)
    major_personalities = serializers.SerializerMethodField()
    primary_currency = serializers.SerializerMethodField()
    
    class Meta:
        model = Region
        fields = [
            'id', 'entity_id', 'name', 'description', 'general_mood', 'terrain_type',
            'size_description', 'world_name', 'world_entity_id', 'location_count',
            'currencies', 'important_personalities', 'religions', 'government_type',
            'cultural_traits', 'major_settlements', 'natural_resources', 'trade_specialties',
            'threats_dangers', 'climate_weather', 'laws_customs', 'festivals_events',
            'military_forces', 'major_personalities', 'primary_currency', 'created_at',
            'updated_at'
        ]
    
    def get_major_personalities(self, obj):
        """Get major personalities with leadership roles."""
        return obj.get_major_personalities()
    
    def get_primary_currency(self, obj):
        """Get the primary currency used in this region."""
        return obj.get_primary_currency() 