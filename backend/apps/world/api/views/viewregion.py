"""
Region API Views
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.world.models import World, Region
from apps.world.api.serializers.serializerregion import (
    RegionCreateSerializer, RegionUpdateSerializer, RegionDetailSerializer,
    RegionListSerializer
)
from apps.permissions.decorators import require_permission_api
from apps.permissions.utils import has_permission


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def region_list(request, world_id):
    """Get list of regions in a world."""
    world = get_object_or_404(World, id=world_id, is_active=True)
    
    # Check if user has view permission on the world
    if not has_permission(request.user, world, 'view'):
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    regions = Region.objects.filter(
        world=world,
        is_active=True
    ).order_by('name')
    
    serializer = RegionListSerializer(regions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@require_permission_api('edit', 'world', 'world_id')
def region_create(request, world_id, world_instance=None):
    """Create a new region in a world."""
    serializer = RegionCreateSerializer(data=request.data)
    if serializer.is_valid():
        region = Region.objects.create(
            world=world_instance,
            **serializer.validated_data
        )
        
        response_serializer = RegionDetailSerializer(region)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@require_permission_api('view', 'world', 'world_id')
def region_detail(request, world_id, region_id, world_instance=None):
    """Get, update, or delete a region."""
    region = get_object_or_404(Region, id=region_id, world=world_instance, is_active=True)
    
    if request.method == 'GET':
        serializer = RegionDetailSerializer(region)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not has_permission(request.user, world_instance, 'edit'):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = RegionUpdateSerializer(region, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_serializer = RegionDetailSerializer(region)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not has_permission(request.user, world_instance, 'delete'):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        region.is_active = False
        region.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@require_permission_api('view', 'world', 'world_id')
def region_statistics(request, world_id, region_id, world_instance=None):
    """Get statistics for a region."""
    region = get_object_or_404(Region, id=region_id, world=world_instance, is_active=True)
    
    stats = {
        'region_id': region.entity_id,
        'region_name': region.name,
        'location_count': region.location_count,
        'major_settlements_count': len(region.major_settlements) if region.major_settlements else 0,
        'important_personalities_count': len(region.important_personalities) if region.important_personalities else 0,
        'threats_dangers_count': len(region.threats_dangers) if region.threats_dangers else 0,
        'trade_specialties_count': len(region.trade_specialties) if region.trade_specialties else 0,
        'military_forces_count': len(region.military_forces) if region.military_forces else 0,
        'festivals_events_count': len(region.festivals_events) if region.festivals_events else 0,
        'created_at': region.created_at,
        'updated_at': region.updated_at
    }
    
    return Response(stats)


@api_view(['GET'])
@require_permission_api('view', 'world', 'world_id')
def region_search(request, world_id, world_instance=None):
    """Search regions by name or description."""
    query = request.GET.get('q', '').strip()
    if not query:
        return Response(
            {'error': 'Query parameter "q" is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    regions = Region.objects.filter(
        world=world_instance,
        is_active=True,
        name__icontains=query
    ).order_by('name')
    
    serializer = RegionListSerializer(regions, many=True)
    return Response(serializer.data) 