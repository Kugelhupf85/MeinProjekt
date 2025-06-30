"""
Location API Views
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from apps.world.services.crudlocation import LocationCRUDService
from apps.world.api.serializers.serializerlocation import (
    LocationCreateSerializer, LocationUpdateSerializer, LocationDetailSerializer,
    LocationListSerializer, LocationStatisticsSerializer
)
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_location(request):
    """
    Create a new location
    
    POST /api/v1/locations/
    """
    try:
        serializer = LocationCreateSerializer(data=request.data)
        if serializer.is_valid():
            location = LocationCRUDService.create_location(serializer.validated_data)
            response_serializer = LocationDetailSerializer(location)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating location: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_location(request, location_id):
    """
    Get location by ID
    
    GET /api/v1/locations/{location_id}/
    """
    try:
        location = LocationCRUDService.get_location_by_id(location_id)
        if not location:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LocationDetailSerializer(location)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error getting location {location_id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_locations(request):
    """
    List locations
    
    GET /api/v1/locations/?region_id={region_id}&world_id={world_id}&location_type={type}
    """
    try:
        region_id = request.GET.get('region_id')
        world_id = request.GET.get('world_id')
        location_type = request.GET.get('location_type')
        active_only = request.GET.get('active_only', 'true').lower() == 'true'
        
        locations = LocationCRUDService.list_locations(
            region_id=region_id, 
            world_id=world_id,
            location_type=location_type,
            active_only=active_only
        )
        
        serializer = LocationListSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error listing locations: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_location(request, location_id):
    """
    Update location
    
    PUT/PATCH /api/v1/locations/{location_id}/
    """
    try:
        serializer = LocationUpdateSerializer(data=request.data)
        if serializer.is_valid():
            location = LocationCRUDService.update_location(location_id, serializer.validated_data)
            if not location:
                return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
            
            response_serializer = LocationDetailSerializer(location)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error updating location {location_id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_location(request, location_id):
    """
    Delete location
    
    DELETE /api/v1/locations/{location_id}/
    """
    try:
        hard_delete = request.GET.get('hard_delete', 'false').lower() == 'true'
        success = LocationCRUDService.delete_location(location_id, hard_delete=hard_delete)
        
        if success:
            return Response({'message': 'Location deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f"Error deleting location {location_id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_locations(request):
    """
    Search locations
    
    GET /api/v1/locations/search/?q={query}&region_id={region_id}&world_id={world_id}
    """
    try:
        query = request.GET.get('q', '')
        region_id = request.GET.get('region_id')
        world_id = request.GET.get('world_id')
        
        if not query:
            return Response({'error': 'Query parameter "q" is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        locations = LocationCRUDService.search_locations(query, region_id=region_id, world_id=world_id)
        serializer = LocationListSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error searching locations: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_location_statistics(request, location_id):
    """
    Get location statistics
    
    GET /api/v1/locations/{location_id}/statistics/
    """
    try:
        stats = LocationCRUDService.get_location_statistics(location_id)
        if not stats:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LocationStatisticsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error getting location statistics {location_id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_locations_by_type(request, location_type):
    """
    Get locations by type
    
    GET /api/v1/locations/type/{location_type}/?world_id={world_id}
    """
    try:
        world_id = request.GET.get('world_id')
        locations = LocationCRUDService.get_locations_by_type(location_type, world_id=world_id)
        
        serializer = LocationListSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error getting locations by type {location_type}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 