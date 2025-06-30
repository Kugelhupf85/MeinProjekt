"""
Views for UserSettings model API.
"""
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404

from ...models import UserSettings, DungeonMaster
from ..serializers import (
    UserSettingsOutputSerializer,
    UserSettingsCreateSerializer,
    UserSettingsUpdateSerializer,
    UISettingUpdateSerializer,
    AISettingUpdateSerializer,
    FeatureFlagUpdateSerializer,
    PrivacySettingUpdateSerializer,
    UserSettingsCompactSerializer,
)


class UserSettingsViewSet(ModelViewSet):
    """
    ViewSet for UserSettings CRUD operations.
    
    Provides:
    - list: GET /api/user-settings/
    - create: POST /api/user-settings/
    - retrieve: GET /api/user-settings/{id}/
    - update: PUT /api/user-settings/{id}/
    - partial_update: PATCH /api/user-settings/{id}/
    - destroy: DELETE /api/user-settings/{id}/
    - my_settings: GET /api/user-settings/my-settings/ (current user's settings)
    - update_ui_setting: PATCH /api/user-settings/{id}/ui-setting/
    - update_ai_setting: PATCH /api/user-settings/{id}/ai-setting/
    - update_feature_flag: PATCH /api/user-settings/{id}/feature-flag/
    - update_privacy_setting: PATCH /api/user-settings/{id}/privacy-setting/
    """
    
    queryset = UserSettings.objects.select_related('dungeonmaster__user').all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action.
        """
        if self.action == 'create':
            return UserSettingsCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserSettingsUpdateSerializer
        elif self.action == 'update_ui_setting':
            return UISettingUpdateSerializer
        elif self.action == 'update_ai_setting':
            return AISettingUpdateSerializer
        elif self.action == 'update_feature_flag':
            return FeatureFlagUpdateSerializer
        elif self.action == 'update_privacy_setting':
            return PrivacySettingUpdateSerializer
        elif self.action == 'list':
            return UserSettingsCompactSerializer
        else:
            return UserSettingsOutputSerializer
    
    def get_queryset(self):
        """
        Filter queryset to only show settings for the current user's DungeonMaster.
        """
        try:
            dungeon_master = DungeonMaster.objects.get(user=self.request.user)
            return self.queryset.filter(dungeonmaster=dungeon_master)
        except DungeonMaster.DoesNotExist:
            return UserSettings.objects.none()
    
    def create(self, request, *args, **kwargs):
        """
        Create UserSettings for the current user's DungeonMaster.
        """
        try:
            dungeon_master = DungeonMaster.objects.get(user=request.user)
        except DungeonMaster.DoesNotExist:
            return Response(
                {'detail': 'DungeonMaster profile not found for current user.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if settings already exist
        if UserSettings.objects.filter(dungeonmaster=dungeon_master).exists():
            return Response(
                {'detail': 'UserSettings already exist for this DungeonMaster.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create UserSettings
        settings_data = serializer.validated_data
        settings_data['dungeonmaster'] = dungeon_master
        
        user_settings = UserSettings.objects.create(**settings_data)
        
        output_serializer = UserSettingsOutputSerializer(user_settings)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        Update UserSettings.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Update UserSettings fields
        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        output_serializer = UserSettingsOutputSerializer(instance)
        return Response(output_serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_settings(self, request):
        """
        Get the current user's UserSettings.
        """
        try:
            dungeon_master = DungeonMaster.objects.get(user=request.user)
            user_settings = UserSettings.objects.get(dungeonmaster=dungeon_master)
            serializer = UserSettingsOutputSerializer(user_settings)
            return Response(serializer.data)
        except DungeonMaster.DoesNotExist:
            return Response(
                {'detail': 'DungeonMaster profile not found for current user.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except UserSettings.DoesNotExist:
            return Response(
                {'detail': 'UserSettings not found for current user.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['patch'])
    def update_ui_setting(self, request, pk=None):
        """
        Update a specific UI setting.
        """
        user_settings = self.get_object()
        serializer = UISettingUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        key = serializer.validated_data['key']
        value = serializer.validated_data['value']
        
        user_settings.set_ui_setting(key, value)
        
        output_serializer = UserSettingsOutputSerializer(user_settings)
        return Response(output_serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_ai_setting(self, request, pk=None):
        """
        Update a specific AI setting.
        """
        user_settings = self.get_object()
        serializer = AISettingUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        key = serializer.validated_data['key']
        value = serializer.validated_data['value']
        
        user_settings.set_ai_setting(key, value)
        
        output_serializer = UserSettingsOutputSerializer(user_settings)
        return Response(output_serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_feature_flag(self, request, pk=None):
        """
        Update a specific feature flag.
        """
        user_settings = self.get_object()
        serializer = FeatureFlagUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        key = serializer.validated_data['key']
        value = serializer.validated_data['value']
        
        user_settings.set_feature_flag(key, value)
        
        output_serializer = UserSettingsOutputSerializer(user_settings)
        return Response(output_serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_privacy_setting(self, request, pk=None):
        """
        Update a specific privacy setting.
        """
        user_settings = self.get_object()
        serializer = PrivacySettingUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        key = serializer.validated_data['key']
        value = serializer.validated_data['value']
        
        user_settings.set_privacy_setting(key, value)
        
        output_serializer = UserSettingsOutputSerializer(user_settings)
        return Response(output_serializer.data)
    
    @action(detail=True, methods=['get'])
    def get_ui_setting(self, request, pk=None):
        """
        Get a specific UI setting value.
        """
        user_settings = self.get_object()
        key = request.query_params.get('key')
        
        if not key:
            return Response(
                {'detail': 'Key parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        value = user_settings.get_ui_setting(key)
        return Response({'key': key, 'value': value})
    
    @action(detail=True, methods=['get'])
    def get_ai_setting(self, request, pk=None):
        """
        Get a specific AI setting value.
        """
        user_settings = self.get_object()
        key = request.query_params.get('key')
        
        if not key:
            return Response(
                {'detail': 'Key parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        value = user_settings.get_ai_setting(key)
        return Response({'key': key, 'value': value})
    
    @action(detail=True, methods=['get'])
    def get_feature_flag(self, request, pk=None):
        """
        Get a specific feature flag value.
        """
        user_settings = self.get_object()
        key = request.query_params.get('key')
        
        if not key:
            return Response(
                {'detail': 'Key parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        value = user_settings.get_feature_flag(key)
        return Response({'key': key, 'value': value})
    
    @action(detail=True, methods=['get'])
    def get_privacy_setting(self, request, pk=None):
        """
        Get a specific privacy setting value.
        """
        user_settings = self.get_object()
        key = request.query_params.get('key')
        
        if not key:
            return Response(
                {'detail': 'Key parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        value = user_settings.get_privacy_setting(key)
        return Response({'key': key, 'value': value})
    
    @action(detail=True, methods=['post'])
    def reset_to_defaults(self, request, pk=None):
        """
        Reset all settings to default values.
        """
        user_settings = self.get_object()
        
        user_settings.ui_settings = UserSettings.get_default_ui_settings()
        user_settings.ai_settings = UserSettings.get_default_ai_settings()
        user_settings.feature_flags = UserSettings.get_default_feature_flags()
        user_settings.privacy_settings = UserSettings.get_default_privacy_settings()
        user_settings.save()
        
        output_serializer = UserSettingsOutputSerializer(user_settings)
        return Response(output_serializer.data) 