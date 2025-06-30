"""
Views for UserKeys model API.
"""
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ...models import UserKeys, DungeonMaster
from ..serializers import (
    UserKeysOutputSerializer,
    UserKeysCreateSerializer,
    UserKeysUpdateSerializer,
    APIKeySetSerializer,
    APIKeyDeleteSerializer,
    APIKeyStatusSerializer,
    UsageStatsSerializer,
    UsageIncrementSerializer,
    UserKeysStatusSerializer,
)


class UserKeysViewSet(ModelViewSet):
    """
    ViewSet for UserKeys CRUD operations.
    
    Provides:
    - list: GET /api/user-keys/
    - create: POST /api/user-keys/
    - retrieve: GET /api/user-keys/{id}/
    - update: PUT /api/user-keys/{id}/
    - partial_update: PATCH /api/user-keys/{id}/
    - destroy: DELETE /api/user-keys/{id}/
    - my_keys: GET /api/user-keys/my-keys/ (current user's keys)
    - set_api_key: POST /api/user-keys/{id}/set-key/
    - delete_api_key: POST /api/user-keys/{id}/delete-key/
    - check_key_status: GET /api/user-keys/{id}/check-status/
    - usage_stats: GET /api/user-keys/{id}/usage-stats/
    - increment_usage: POST /api/user-keys/{id}/increment-usage/
    - reset_usage: POST /api/user-keys/{id}/reset-usage/
    """
    
    queryset = UserKeys.objects.select_related('dungeonmaster__user').all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action.
        """
        if self.action == 'create':
            return UserKeysCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserKeysUpdateSerializer
        elif self.action == 'set_api_key':
            return APIKeySetSerializer
        elif self.action == 'delete_api_key':
            return APIKeyDeleteSerializer
        elif self.action == 'check_key_status':
            return APIKeyStatusSerializer
        elif self.action == 'usage_stats':
            return UsageStatsSerializer
        elif self.action == 'increment_usage':
            return UsageIncrementSerializer
        elif self.action == 'list':
            return UserKeysStatusSerializer
        else:
            return UserKeysOutputSerializer
    
    def get_queryset(self):
        """
        Filter queryset to only show keys for the current user's DungeonMaster.
        """
        try:
            dungeon_master = DungeonMaster.objects.get(user=self.request.user)
            return self.queryset.filter(dungeonmaster=dungeon_master)
        except DungeonMaster.DoesNotExist:
            return UserKeys.objects.none()
    
    def create(self, request, *args, **kwargs):
        """
        Create UserKeys for the current user's DungeonMaster.
        """
        try:
            dungeon_master = DungeonMaster.objects.get(user=request.user)
        except DungeonMaster.DoesNotExist:
            return Response(
                {'detail': 'DungeonMaster profile not found for current user.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if keys already exist
        if UserKeys.objects.filter(dungeonmaster=dungeon_master).exists():
            return Response(
                {'detail': 'UserKeys already exist for this DungeonMaster.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create UserKeys
        keys_data = serializer.validated_data
        keys_data['dungeonmaster'] = dungeon_master
        
        user_keys = UserKeys.objects.create(**keys_data)
        
        output_serializer = UserKeysOutputSerializer(user_keys)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        Update UserKeys (status and metadata only, not encrypted keys).
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Update UserKeys fields
        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        output_serializer = UserKeysOutputSerializer(instance)
        return Response(output_serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_keys(self, request):
        """
        Get the current user's UserKeys.
        """
        try:
            dungeon_master = DungeonMaster.objects.get(user=request.user)
            user_keys = UserKeys.objects.get(dungeonmaster=dungeon_master)
            serializer = UserKeysOutputSerializer(user_keys)
            return Response(serializer.data)
        except DungeonMaster.DoesNotExist:
            return Response(
                {'detail': 'DungeonMaster profile not found for current user.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except UserKeys.DoesNotExist:
            return Response(
                {'detail': 'UserKeys not found for current user.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def set_api_key(self, request, pk=None):
        """
        Set/update an encrypted API key for a specific provider.
        
        Note: This is a placeholder implementation. In production, you would:
        1. Use proper encryption (pgcrypto or similar)
        2. Validate the API key with the provider
        3. Store the encrypted version
        """
        user_keys = self.get_object()
        serializer = APIKeySetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        provider = serializer.validated_data['provider']
        api_key = serializer.validated_data['api_key']
        
        # TODO: Implement proper encryption here
        # For now, we'll just simulate setting the encrypted key
        encrypted_key = api_key.encode('utf-8')  # This should be properly encrypted
        
        # Set the encrypted key
        key_field = f"{provider}_key_encrypted"
        setattr(user_keys, key_field, encrypted_key)
        
        # Update status and validation timestamp
        user_keys.set_key_status(provider, 'configured')
        user_keys.set_last_validated(provider)
        user_keys.last_key_update = timezone.now()
        user_keys.save()
        
        output_serializer = UserKeysOutputSerializer(user_keys)
        return Response(output_serializer.data)
    
    @action(detail=True, methods=['post'])
    def delete_api_key(self, request, pk=None):
        """
        Delete an API key for a specific provider.
        """
        user_keys = self.get_object()
        serializer = APIKeyDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        provider = serializer.validated_data['provider']
        
        # Clear the encrypted key
        key_field = f"{provider}_key_encrypted"
        setattr(user_keys, key_field, None)
        
        # Update status and clear validation timestamp
        user_keys.set_key_status(provider, 'not_configured')
        validated_field = f"{provider}_last_validated"
        setattr(user_keys, validated_field, None)
        user_keys.last_key_update = timezone.now()
        user_keys.save()
        
        output_serializer = UserKeysOutputSerializer(user_keys)
        return Response(output_serializer.data)
    
    @action(detail=True, methods=['get'])
    def check_key_status(self, request, pk=None):
        """
        Check the status of API keys for a specific provider or all providers.
        """
        user_keys = self.get_object()
        provider = request.query_params.get('provider')
        
        if provider:
            if provider not in ['openai', 'anthropic', 'google', 'deepseek']:
                return Response(
                    {'detail': 'Invalid provider.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            status_info = {
                'provider': provider,
                'status': user_keys.get_key_status(provider),
                'has_key': user_keys.has_encrypted_key(provider),
                'last_validated': user_keys.get_last_validated(provider),
            }
            return Response(status_info)
        else:
            # Return status for all providers
            all_status = {}
            for p in ['openai', 'anthropic', 'google', 'deepseek']:
                all_status[p] = {
                    'status': user_keys.get_key_status(p),
                    'has_key': user_keys.has_encrypted_key(p),
                    'last_validated': user_keys.get_last_validated(p),
                }
            return Response(all_status)
    
    @action(detail=True, methods=['get'])
    def usage_stats(self, request, pk=None):
        """
        Get usage statistics for API providers.
        """
        user_keys = self.get_object()
        provider = request.query_params.get('provider')
        
        if provider:
            if provider not in ['openai', 'anthropic', 'google', 'deepseek']:
                return Response(
                    {'detail': 'Invalid provider.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            stats = user_keys.get_usage_stats(provider)
            return Response({'provider': provider, 'stats': stats})
        else:
            # Return stats for all providers
            return Response({'usage_statistics': user_keys.usage_statistics})
    
    @action(detail=True, methods=['post'])
    def increment_usage(self, request, pk=None):
        """
        Increment usage counter for a specific provider.
        """
        user_keys = self.get_object()
        serializer = UsageIncrementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        provider = serializer.validated_data['provider']
        user_keys.increment_usage(provider)
        
        stats = user_keys.get_usage_stats(provider)
        return Response({'provider': provider, 'stats': stats})
    
    @action(detail=True, methods=['post'])
    def reset_usage(self, request, pk=None):
        """
        Reset usage statistics for a specific provider or all providers.
        """
        user_keys = self.get_object()
        provider = request.data.get('provider')
        
        if provider:
            if provider not in ['openai', 'anthropic', 'google', 'deepseek']:
                return Response(
                    {'detail': 'Invalid provider.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user_keys.reset_daily_usage(provider)
            stats = user_keys.get_usage_stats(provider)
            return Response({'provider': provider, 'stats': stats})
        else:
            # Reset all providers
            user_keys.reset_daily_usage()
            return Response({'usage_statistics': user_keys.usage_statistics})
    
    @action(detail=True, methods=['post'])
    def validate_key(self, request, pk=None):
        """
        Validate an API key with the provider.
        
        Note: This is a placeholder. In production, you would:
        1. Decrypt the stored key
        2. Make a test API call to the provider
        3. Update the status based on the result
        """
        user_keys = self.get_object()
        provider = request.data.get('provider')
        
        if not provider or provider not in ['openai', 'anthropic', 'google', 'deepseek']:
            return Response(
                {'detail': 'Valid provider is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user_keys.has_encrypted_key(provider):
            return Response(
                {'detail': f'No API key configured for {provider}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implement actual validation with the provider's API
        # For now, we'll just update the validation timestamp
        user_keys.set_last_validated(provider)
        user_keys.set_key_status(provider, 'configured')
        
        output_serializer = UserKeysOutputSerializer(user_keys)
        return Response(output_serializer.data)
    
    @action(detail=True, methods=['get'])
    def configured_providers(self, request, pk=None):
        """
        Get a list of configured providers.
        """
        user_keys = self.get_object()
        providers = user_keys.get_configured_providers()
        return Response({'configured_providers': providers}) 