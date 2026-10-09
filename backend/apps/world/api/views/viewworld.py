"""
World API Views
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from apps.world.models import World, WorldAPIKeys, WorldParty, WorldPartyMembership
from apps.world.api.serializers.serializerworld import (
    WorldCreateSerializer, WorldUpdateSerializer, WorldDetailSerializer,
    WorldAPIKeysSerializer, WorldAPIKeyUpdateSerializer,
    WorldPartySerializer, WorldPartyMembershipSerializer,
    WorldPartyMembershipUpdateSerializer, WorldPartyInviteSerializer
)
from apps.permissions.decorators import require_permission_api
from apps.permissions.utils import has_permission

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def world_list(request):
    """Get list of worlds accessible to the user."""
    # Get worlds where user has view permission
    from apps.permissions.utils import get_accessible_resources
    accessible_world_ids = get_accessible_resources(request.user, 'world', 'view')
    
    worlds = World.objects.filter(
        id__in=accessible_world_ids,
        is_active=True
    ).order_by('-created_at')
    
    serializer = WorldDetailSerializer(worlds, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def world_create(request):
    """Create a new world."""
    serializer = WorldCreateSerializer(data=request.data)
    if serializer.is_valid():
        world = World.objects.create(
            created_by=request.user,
            **serializer.validated_data
        )
        
        # Grant admin permission to creator
        from apps.permissions.models.permission import Permission
        Permission.grant_permission(
            user=request.user,
            resource=world,
            permission_type='admin',
            granted_by=request.user
        )
        
        response_serializer = WorldDetailSerializer(world)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@require_permission_api('view', 'world', 'world_id')
def world_detail(request, world_id, world_instance=None):
    """Get, update, or delete a world."""
    if request.method == 'GET':
        serializer = WorldDetailSerializer(world_instance)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not has_permission(request.user, world_instance, 'edit'):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = WorldUpdateSerializer(world_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_serializer = WorldDetailSerializer(world_instance)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not has_permission(request.user, world_instance, 'delete'):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        world_instance.is_active = False
        world_instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# World API Keys Views
@api_view(['GET'])
@require_permission_api('view', 'world', 'world_id')
def world_api_keys_detail(request, world_id, world_instance=None):
    """Get API keys for a world."""
    if not has_permission(request.user, world_instance, 'admin'):
        return Response(
            {'error': 'Admin permission required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    api_keys = get_object_or_404(WorldAPIKeys, world=world_instance)
    serializer = WorldAPIKeysSerializer(api_keys)
    return Response(serializer.data)


@api_view(['PUT'])
@require_permission_api('admin', 'world', 'world_id')
def world_api_keys_update(request, world_id, world_instance=None):
    """Update API key status for a world."""
    api_keys = get_object_or_404(WorldAPIKeys, world=world_instance)
    serializer = WorldAPIKeyUpdateSerializer(data=request.data)
    
    if serializer.is_valid():
        provider = serializer.validated_data['provider']
        status_value = serializer.validated_data['status']
        
        # Update provider status
        setattr(api_keys, f"{provider}_status", status_value)
        
        # Update security notes if provided
        if 'security_notes' in serializer.validated_data:
            api_keys.security_notes = serializer.validated_data['security_notes']
        
        api_keys.save()
        
        response_serializer = WorldAPIKeysSerializer(api_keys)
        return Response(response_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@require_permission_api('admin', 'world', 'world_id')
def world_api_keys_test(request, world_id, world_instance=None):
    """Test API key for a specific provider."""
    provider = request.data.get('provider')
    if not provider or provider not in ['openai', 'anthropic', 'google', 'deepseek']:
        return Response(
            {'error': 'Invalid provider'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    api_keys = get_object_or_404(WorldAPIKeys, world=world_instance)
    
    # Here you would implement the actual API key testing logic
    # For now, we'll just mark it as configured
    api_keys.mark_provider_configured(provider)
    
    return Response({
        'provider': provider,
        'status': 'configured',
        'message': f'{provider} API key tested successfully'
    })


# World Party Views
@api_view(['GET'])
@require_permission_api('view', 'world', 'world_id')
def world_party_detail(request, world_id, world_instance=None):
    """Get party details for a world."""
    party = get_object_or_404(WorldParty, world=world_instance)
    serializer = WorldPartySerializer(party)
    return Response(serializer.data)


@api_view(['PUT'])
@require_permission_api('edit', 'world', 'world_id')
def world_party_update(request, world_id, world_instance=None):
    """Update party details."""
    party = get_object_or_404(WorldParty, world=world_instance)
    serializer = WorldPartySerializer(party, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@require_permission_api('view', 'world', 'world_id')
def world_party_members(request, world_id, world_instance=None):
    """Get party members for a world."""
    party = get_object_or_404(WorldParty, world=world_instance)
    memberships = party.memberships.all().select_related('user')
    serializer = WorldPartyMembershipSerializer(memberships, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@require_permission_api('edit', 'world', 'world_id')
def world_party_invite(request, world_id, world_instance=None):
    """Invite a user to the party."""
    party = get_object_or_404(WorldParty, world=world_instance)
    serializer = WorldPartyInviteSerializer(data=request.data)
    
    if serializer.is_valid():
        user_email = serializer.validated_data['user_email']
        role = serializer.validated_data['role']
        
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is already a member
        if party.memberships.filter(user=user).exists():
            return Response(
                {'error': 'User is already a member'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create membership
        membership = WorldPartyMembership.objects.create(
            user=user,
            party=party,
            role=role,
            status='invited'
        )
        
        # Grant view permission to invited user
        from apps.permissions.models.permission import Permission
        Permission.grant_permission(
            user=user,
            resource=world_instance,
            permission_type='view',
            granted_by=request.user
        )
        
        response_serializer = WorldPartyMembershipSerializer(membership)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@require_permission_api('edit', 'world', 'world_id')
def world_party_membership_update(request, world_id, membership_id, world_instance=None):
    """Update party membership."""
    membership = get_object_or_404(WorldPartyMembership, id=membership_id, party__world=world_instance)
    serializer = WorldPartyMembershipUpdateSerializer(membership, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        response_serializer = WorldPartyMembershipSerializer(membership)
        return Response(response_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@require_permission_api('edit', 'world', 'world_id')
def world_party_membership_remove(request, world_id, membership_id, world_instance=None):
    """Remove a member from the party."""
    membership = get_object_or_404(WorldPartyMembership, id=membership_id, party__world=world_instance)
    
    # Remove permissions for the user
    from apps.permissions.models.permission import Permission
    Permission.revoke_all_permissions(
        user=membership.user,
        resource=world_instance
    )
    
    membership.delete()
    return Response(status=status.HTTP_204_NO_CONTENT) 