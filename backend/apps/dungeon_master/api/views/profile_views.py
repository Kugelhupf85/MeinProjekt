"""
Views for DungeonMaster profile management with secure forms.
"""
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404

from ...models import DungeonMaster, UserSettings, UserKeys
from ..serializers import (
    DungeonMasterOutputSerializer,
    DungeonMasterUpdateSerializer,
    UserUpdateSerializer,
    UserSettingsOutputSerializer,
    UserSettingsUpdateSerializer,
    UserKeysStatusSerializer,
)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def profile_settings(request):
    """
    Secure endpoint for profile settings management.
    
    GET: Retrieve complete profile data for settings display
    POST: Update profile data with validation
    """
    try:
        dungeon_master = DungeonMaster.objects.select_related('user').get(
            user=request.user
        )
    except DungeonMaster.DoesNotExist:
        return Response(
            {'detail': 'DungeonMaster profile not found for current user.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        # Return complete profile data for settings form
        try:
            user_settings = UserSettings.objects.get(dungeonmaster=dungeon_master)
        except UserSettings.DoesNotExist:
            user_settings = None
        
        try:
            user_keys = UserKeys.objects.get(dungeonmaster=dungeon_master)
        except UserKeys.DoesNotExist:
            user_keys = None
        
        profile_data = {
            'dungeon_master': DungeonMasterOutputSerializer(dungeon_master).data,
            'settings': UserSettingsOutputSerializer(user_settings).data if user_settings else None,
            'keys_status': UserKeysStatusSerializer(user_keys).data if user_keys else None,
        }
        
        return Response(profile_data)
    
    elif request.method == 'POST':
        # Update profile data with validation
        with transaction.atomic():
            updated_data = {}
            
            # Update DungeonMaster profile if data provided
            if 'dungeon_master' in request.data:
                dm_serializer = DungeonMasterUpdateSerializer(
                    dungeon_master,
                    data=request.data['dungeon_master'],
                    partial=True
                )
                if dm_serializer.is_valid():
                    for attr, value in dm_serializer.validated_data.items():
                        setattr(dungeon_master, attr, value)
                    dungeon_master.save()
                    updated_data['dungeon_master'] = DungeonMasterOutputSerializer(dungeon_master).data
                else:
                    return Response(dm_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Update User information if data provided
            if 'user' in request.data:
                user_serializer = UserUpdateSerializer(
                    dungeon_master.user,
                    data=request.data['user'],
                    partial=True,
                    context={'request': request}
                )
                if user_serializer.is_valid():
                    for attr, value in user_serializer.validated_data.items():
                        setattr(dungeon_master.user, attr, value)
                    dungeon_master.user.save()
                    updated_data['user'] = user_serializer.validated_data
                else:
                    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Update UserSettings if data provided
            if 'settings' in request.data:
                try:
                    user_settings = UserSettings.objects.get(dungeonmaster=dungeon_master)
                except UserSettings.DoesNotExist:
                    user_settings = UserSettings.objects.create(dungeonmaster=dungeon_master)
                
                settings_serializer = UserSettingsUpdateSerializer(
                    user_settings,
                    data=request.data['settings'],
                    partial=True
                )
                if settings_serializer.is_valid():
                    for attr, value in settings_serializer.validated_data.items():
                        setattr(user_settings, attr, value)
                    user_settings.save()
                    updated_data['settings'] = UserSettingsOutputSerializer(user_settings).data
                else:
                    return Response(settings_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': 'Profile updated successfully',
            'updated_data': updated_data
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_summary(request):
    """
    Get a summary of the current user's profile for dashboard display.
    """
    try:
        dungeon_master = DungeonMaster.objects.select_related('user').get(
            user=request.user
        )
    except DungeonMaster.DoesNotExist:
        return Response(
            {'detail': 'DungeonMaster profile not found for current user.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get settings and keys status
    try:
        user_settings = UserSettings.objects.get(dungeonmaster=dungeon_master)
        theme = user_settings.get_ui_setting('theme', 'dark')
        language = user_settings.get_ui_setting('language', 'de')
    except UserSettings.DoesNotExist:
        theme = 'dark'
        language = 'de'
    
    try:
        user_keys = UserKeys.objects.get(dungeonmaster=dungeon_master)
        configured_providers = user_keys.get_configured_providers()
    except UserKeys.DoesNotExist:
        configured_providers = []
    
    summary = {
        'entity_id': dungeon_master.entity_id,
        'display_name': dungeon_master.display_name or dungeon_master.user.username,
        'email': dungeon_master.user.email,
        'experience_level': dungeon_master.experience_level,
        'is_public': dungeon_master.is_public,
        'theme': theme,
        'language': language,
        'configured_providers': configured_providers,
        'last_active': dungeon_master.last_active,
        'created_at': dungeon_master.created_at,
    }
    
    return Response(summary)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def quick_setting_update(request):
    """
    Quick update for individual settings (theme, language, etc.).
    """
    try:
        dungeon_master = DungeonMaster.objects.get(user=request.user)
    except DungeonMaster.DoesNotExist:
        return Response(
            {'detail': 'DungeonMaster profile not found for current user.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    setting_type = request.data.get('type')  # 'ui', 'ai', 'feature', 'privacy'
    key = request.data.get('key')
    value = request.data.get('value')
    
    if not all([setting_type, key]):
        return Response(
            {'detail': 'Type and key are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user_settings = UserSettings.objects.get(dungeonmaster=dungeon_master)
    except UserSettings.DoesNotExist:
        user_settings = UserSettings.objects.create(dungeonmaster=dungeon_master)
    
    if setting_type == 'ui':
        user_settings.set_ui_setting(key, value)
    elif setting_type == 'ai':
        user_settings.set_ai_setting(key, value)
    elif setting_type == 'feature':
        user_settings.set_feature_flag(key, value)
    elif setting_type == 'privacy':
        user_settings.set_privacy_setting(key, value)
    else:
        return Response(
            {'detail': 'Invalid setting type.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({
        'message': f'{setting_type.title()} setting updated successfully',
        'key': key,
        'value': value
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def initialize_profile(request):
    """
    Initialize complete profile structure for new users.
    """
    try:
        dungeon_master = DungeonMaster.objects.get(user=request.user)
    except DungeonMaster.DoesNotExist:
        return Response(
            {'detail': 'DungeonMaster profile not found for current user.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    with transaction.atomic():
        # Create UserSettings if not exists
        user_settings, settings_created = UserSettings.objects.get_or_create(
            dungeonmaster=dungeon_master
        )
        
        # Create UserKeys if not exists
        user_keys, keys_created = UserKeys.objects.get_or_create(
            dungeonmaster=dungeon_master
        )
    
    return Response({
        'message': 'Profile initialized successfully',
        'settings_created': settings_created,
        'keys_created': keys_created,
        'profile': DungeonMasterOutputSerializer(dungeon_master).data
    }) 