"""
Serializers for Adventure campaign management.
"""
from rest_framework import serializers
from ...models import Adventure


class AdventureCreateSerializer(serializers.Serializer):
    """
    Serializer for creating new Adventures.
    """
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    game_system = serializers.CharField(max_length=100, default='D&D 5e')
    adventure_settings = serializers.JSONField(required=False, default=dict)
    world_building = serializers.JSONField(required=False, default=dict)
    player_count = serializers.IntegerField(min_value=0, max_value=10, default=0)


class AdventureOutputSerializer(serializers.ModelSerializer):
    """
    Serializer for Adventure output with all fields.
    """
    dungeon_master_username = serializers.CharField(source='dungeon_master.user.username', read_only=True)
    dungeon_master_entity_id = serializers.CharField(source='dungeon_master.entity_id', read_only=True)
    session_count = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Adventure
        fields = [
            'entity_id',
            'name',
            'description',
            'game_system',
            'adventure_settings',
            'world_building',
            'session_notes',
            'character_sheets',
            'campaign_timeline',
            'rules_modifications',
            'status',
            'is_public',
            'created_at',
            'updated_at',
            'started_at',
            'completed_at',
            'current_session',
            'total_sessions',
            'player_count',
            'dungeon_master_username',
            'dungeon_master_entity_id',
            'session_count',
            'is_active'
        ]
        read_only_fields = [
            'entity_id',
            'created_at',
            'updated_at',
            'started_at',
            'completed_at',
            'dungeon_master_username',
            'dungeon_master_entity_id',
            'session_count',
            'is_active'
        ]


class AdventureListSerializer(serializers.ModelSerializer):
    """
    Serializer for Adventure list view with essential fields.
    """
    dungeon_master_username = serializers.CharField(source='dungeon_master.user.username', read_only=True)
    session_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Adventure
        fields = [
            'entity_id',
            'name',
            'description',
            'game_system',
            'status',
            'is_public',
            'player_count',
            'current_session',
            'total_sessions',
            'created_at',
            'updated_at',
            'dungeon_master_username',
            'session_count'
        ]
        read_only_fields = '__all__' 