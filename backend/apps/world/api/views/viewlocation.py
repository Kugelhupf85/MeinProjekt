"""
Location API Views
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.world.models import World, Region, Location
from apps.world.api.serializers.serializerlocation import (
    LocationCreateSerializer, LocationUpdateSerializer, LocationDetailSerializer,
    LocationListSerializer
)
from apps.permissions.decorators import require_permission_api
from apps.permissions.utils import has_permission


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def location_list(request, world_id, region_id=None):
    """Get list of locations in a world or region."""
    world = get_object_or_404(World, id=world_id, is_active=True)
    
    # Check if user has view permission on the world
    if not has_permission(request.user, world, 'view'):
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    if region_id:
        # Get locations in specific region
        region = get_object_or_404(Region, id=region_id, world=world, is_active=True)
        locations = Location.objects.filter(
            region=region,
            is_active=True
        ).order_by('name')
    else:
        # Get all locations in world
        locations = Location.objects.filter(
            region__world=world,
            is_active=True
        ).select_related('region').order_by('region__name', 'name')
    
    serializer = LocationListSerializer(locations, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@require_permission_api('edit', 'world', 'world_id')
def location_create(request, world_id, region_id, world_instance=None):
    """Create a new location in a region."""
    region = get_object_or_404(Region, id=region_id, world=world_instance, is_active=True)
    
    serializer = LocationCreateSerializer(data=request.data)
    if serializer.is_valid():
        location = Location.objects.create(
            region=region,
            **serializer.validated_data
        )
        
        response_serializer = LocationDetailSerializer(location)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@require_permission_api('view', 'world', 'world_id')
def location_detail(request, world_id, region_id, location_id, world_instance=None):
    """Get, update, or delete a location."""
    region = get_object_or_404(Region, id=region_id, world=world_instance, is_active=True)
    location = get_object_or_404(Location, id=location_id, region=region, is_active=True)
    
    if request.method == 'GET':
        serializer = LocationDetailSerializer(location)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not has_permission(request.user, world_instance, 'edit'):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = LocationUpdateSerializer(location, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_serializer = LocationDetailSerializer(location)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not has_permission(request.user, world_instance, 'delete'):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        location.is_active = False
        location.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@require_permission_api('view', 'world', 'world_id')
def location_statistics(request, world_id, region_id, location_id, world_instance=None):
    """Get statistics for a location."""
    region = get_object_or_404(Region, id=region_id, world=world_instance, is_active=True)
    location = get_object_or_404(Location, id=location_id, region=region, is_active=True)
    
    stats = {
        'location_id': location.entity_id,
        'location_name': location.name,
        'location_type': location.location_type,
        'full_path': location.full_path,
        'important_personalities_count': len(location.important_personalities) if location.important_personalities else 0,
        'services_available_count': len(location.services_available) if location.services_available else 0,
        'notable_features_count': len(location.notable_features) if location.notable_features else 0,
        'secrets_hidden_count': len(location.secrets_hidden) if location.secrets_hidden else 0,
        'encounters_possible_count': len(location.encounters_possible) if location.encounters_possible else 0,
        'items_treasures_count': len(location.items_treasures) if location.items_treasures else 0,
        'defenses_security_count': len(location.defenses_security) if location.defenses_security else 0,
        'quest_opportunities_count': len(location.quest_opportunities) if location.quest_opportunities else 0,
        'current_events_count': len(location.current_events) if location.current_events else 0,
        'rumors_information_count': len(location.rumors_information) if location.rumors_information else 0,
        'created_at': location.created_at,
        'updated_at': location.updated_at
    }
    
    return Response(stats)


@api_view(['GET'])
@require_permission_api('view', 'world', 'world_id')
def location_search(request, world_id, world_instance=None):
    """Search locations by name, description, or type."""
    query = request.GET.get('q', '').strip()
    location_type = request.GET.get('type', '').strip()
    
    if not query and not location_type:
        return Response(
            {'error': 'Query parameter "q" or "type" is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    locations = Location.objects.filter(
        region__world=world_instance,
        is_active=True
    ).select_related('region')
    
    if query:
        locations = locations.filter(name__icontains=query)
    
    if location_type:
        locations = locations.filter(location_type=location_type)
    
    locations = locations.order_by('region__name', 'name')
    
    serializer = LocationListSerializer(locations, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@require_permission_api('view', 'world', 'world_id')
def location_by_type(request, world_id, location_type, world_instance=None):
    """Get all locations of a specific type in a world."""
    if location_type not in dict(Location.LOCATION_TYPES):
        return Response(
            {'error': 'Invalid location type'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    locations = Location.objects.filter(
        region__world=world_instance,
        location_type=location_type,
        is_active=True
    ).select_related('region').order_by('region__name', 'name')
    
    serializer = LocationListSerializer(locations, many=True)
    return Response(serializer.data) 