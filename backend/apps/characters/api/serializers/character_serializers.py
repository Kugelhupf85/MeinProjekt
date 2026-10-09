"""
Character API Serializers
DRF serializers for character management endpoints
"""

from rest_framework import serializers
from apps.characters.models import (
    Character, CharacterRuleSetData, RuleSet, DSARace, DSACulture, DSAProfession,
    DSAAdvantage, DSADisadvantage, CharacterAdvantage, CharacterDisadvantage
)


class RuleSetSerializer(serializers.ModelSerializer):
    """Serializer für RuleSet-Model"""
    
    class Meta:
        model = RuleSet
        fields = ['id', 'name', 'display_name', 'version', 'attribute_schema', 'default_values', 'is_active']


class DSARaceSerializer(serializers.ModelSerializer):
    """Serializer für DSA Race-Model"""
    
    class Meta:
        model = DSARace
        fields = ['id', 'name', 'attribute_modifiers', 'granted_special_abilities', 'starting_modifications', 
                 'generation_point_cost', 'restrictions', 'description', 'is_active']


class DSACultureSerializer(serializers.ModelSerializer):
    """Serializer für DSA Culture-Model"""
    
    class Meta:
        model = DSACulture
        fields = ['id', 'name', 'language_bonuses', 'script_bonuses', 'talent_modifications', 
                 'typical_professions', 'social_status_min', 'social_status_max', 'restrictions', 
                 'starting_equipment_modifications', 'description', 'is_active']


class DSAProfessionSerializer(serializers.ModelSerializer):
    """Serializer für DSA Profession-Model"""
    
    class Meta:
        model = DSAProfession
        fields = ['id', 'name', 'category', 'attribute_requirements', 'talent_bonuses', 
                 'granted_special_abilities', 'starting_equipment', 'generation_point_cost', 
                 'restrictions', 'starting_values', 'advancement_options', 'description', 'is_active']


class DSAAdvantageSerializer(serializers.ModelSerializer):
    """Serializer für DSA Advantage-Model"""
    
    class Meta:
        model = DSAAdvantage
        fields = ['id', 'name', 'gp_cost_base', 'gp_cost_per_level', 'max_levels', 'requirements', 
                 'effects', 'incompatible_with', 'category', 'restrictions', 'scaling_effects', 'description', 'is_active']


class DSADisadvantageSerializer(serializers.ModelSerializer):
    """Serializer für DSA Disadvantage-Model"""
    
    class Meta:
        model = DSADisadvantage
        fields = ['id', 'name', 'gp_gain_base', 'gp_gain_per_level', 'max_levels', 'effects', 
                 'incompatible_with', 'category', 'restrictions', 'scaling_effects', 'requirements', 'description', 'is_active']


class CharacterAdvantageSerializer(serializers.ModelSerializer):
    """Serializer für Character-Advantage-Verbindung"""
    
    advantage_name = serializers.CharField(source='advantage.name', read_only=True)
    gp_cost = serializers.IntegerField(read_only=True)
    total_effects = serializers.JSONField(read_only=True)
    
    class Meta:
        model = CharacterAdvantage
        fields = ['id', 'advantage', 'advantage_name', 'level', 'custom_modifiers', 'acquired_at', 
                 'acquisition_notes', 'is_valid', 'validation_errors', 'gp_cost', 'total_effects']


class CharacterDisadvantageSerializer(serializers.ModelSerializer):
    """Serializer für Character-Disadvantage-Verbindung"""
    
    disadvantage_name = serializers.CharField(source='disadvantage.name', read_only=True)
    gp_gain = serializers.IntegerField(read_only=True)
    total_effects = serializers.JSONField(read_only=True)
    
    class Meta:
        model = CharacterDisadvantage
        fields = ['id', 'disadvantage', 'disadvantage_name', 'level', 'custom_modifiers', 'acquired_at', 
                 'acquisition_notes', 'is_valid', 'validation_errors', 'gp_gain', 'total_effects']


class CharacterRuleSetDataSerializer(serializers.ModelSerializer):
    """Serializer für Character RuleSet-spezifische Daten"""
    
    generation_points_used = serializers.IntegerField(read_only=True)
    generation_points_remaining = serializers.IntegerField(read_only=True)
    is_generation_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CharacterRuleSetData
        fields = ['id', 'generation_points_max', 'generation_points_attributes_max', 'attribute_maximum',
                 'xp_total', 'xp_current', 'level', 'birthday', 'age', 'weight', 'height', 'gender',
                 'hair_color', 'eye_color', 'magic_resistance', 'life_energy', 'endurance', 
                 'astral_energy', 'karma_energy', 'attack_base', 'parade_base', 'ranged_combat_base',
                 'initiative', 'social_status', 'guild_membership', 'extended_data',
                 'generation_points_used', 'generation_points_remaining', 'is_generation_valid']


class CharacterListSerializer(serializers.ModelSerializer):
    """Serializer für Character-Listen"""
    
    rule_set_name = serializers.CharField(source='rule_set.display_name', read_only=True)
    world_name = serializers.CharField(source='world.name', read_only=True)
    
    class Meta:
        model = Character
        fields = ['id', 'name', 'status', 'rule_set_name', 'world_name', 'created_at', 'updated_at']


class CharacterDetailSerializer(serializers.ModelSerializer):
    """Serializer für Character-Details"""
    
    rule_set = RuleSetSerializer(read_only=True)
    world_name = serializers.CharField(source='world.name', read_only=True)
    ruleset_data = CharacterRuleSetDataSerializer(read_only=True)
    character_advantages = CharacterAdvantageSerializer(many=True, read_only=True)
    character_disadvantages = CharacterDisadvantageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Character
        fields = ['id', 'name', 'status', 'rule_set', 'world_name', 'core_attributes', 
                 'ruleset_data', 'character_advantages', 'character_disadvantages', 'created_at', 'updated_at']


class CharacterCreateSerializer(serializers.ModelSerializer):
    """Serializer für Character-Erstellung"""
    
    class Meta:
        model = Character
        fields = ['name', 'rule_set', 'core_attributes']
    
    def validate(self, data):
        """Validierung der Character-Daten"""
        # Basis-Validierung
        if not data.get('name'):
            raise serializers.ValidationError("Name ist erforderlich")
        
        if not data.get('core_attributes'):
            raise serializers.ValidationError("Core attributes sind erforderlich")
        
        # RuleSet-Validierung
        rule_set = data.get('rule_set')
        if rule_set:
            schema = rule_set.get_attribute_schema()
            if schema:
                required_attrs = schema.get('required', [])
                for attr in required_attrs:
                    if attr not in data.get('core_attributes', {}):
                        raise serializers.ValidationError(f"Required attribute '{attr}' is missing")
        
        return data


class CharacterUpdateSerializer(serializers.ModelSerializer):
    """Serializer für Character-Updates"""
    
    class Meta:
        model = Character
        fields = ['name', 'status', 'core_attributes']
    
    def validate(self, data):
        """Validierung der Update-Daten"""
        # Status-Validierung
        status = data.get('status')
        if status and status not in ['draft', 'active', 'archived']:
            raise serializers.ValidationError("Invalid status")
        
        return data


class ReferenceDataSerializer(serializers.Serializer):
    """Serializer für Referenz-Daten"""
    
    races = DSARaceSerializer(many=True)
    cultures = DSACultureSerializer(many=True)
    professions = DSAProfessionSerializer(many=True)
    advantages = DSAAdvantageSerializer(many=True)
    disadvantages = DSADisadvantageSerializer(many=True)


class CharacterValidationSerializer(serializers.Serializer):
    """Serializer für Character-Validierung"""
    
    character_data = serializers.JSONField()
    
    def validate_character_data(self, value):
        """Validierung der Character-Daten"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Character data must be a dictionary")
        
        required_fields = ['name', 'core_attributes']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Required field '{field}' is missing")
        
        return value


class CharacterCalculationSerializer(serializers.Serializer):
    """Serializer für Character-Berechnungen"""
    
    core_attributes = serializers.JSONField()
    race_modifiers = serializers.JSONField(required=False, default=dict)
    advantages = serializers.JSONField(required=False, default=list)
    
    def validate_core_attributes(self, value):
        """Validierung der Core-Attribute"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Core attributes must be a dictionary")
        
        required_attrs = ['MU', 'KL', 'IN', 'CH', 'FF', 'GE', 'KO', 'KK']
        for attr in required_attrs:
            if attr not in value:
                raise serializers.ValidationError(f"Required attribute '{attr}' is missing")
            if not isinstance(value[attr], int):
                raise serializers.ValidationError(f"Attribute '{attr}' must be an integer")
        
        return value 