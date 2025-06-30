"""
Region API Views
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from apps.world.services.crudregion import RegionCRUDService
from apps.world.api.serializers.serializerregion import (
    RegionCreateSerializer, RegionUpdateSerializer, RegionDetailSerializer,
    RegionListSerializer, RegionStatisticsSerializer
)
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_region(request):
    """
    Create a new region
    
    POST /api/v1/regions/
    """
    try:
        serializer = RegionCreateSerializer(data=request.data)
        if serializer.is_valid():
            region = RegionCRUDService.create_region(serializer.validated_data)
            response_serializer = RegionDetailSerializer(region)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating region: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_region(request, region_id):
    """
    Get region by ID
    
    GET /api/v1/regions/{region_id}/
    """
    try:
        region = RegionCRUDService.get_region_by_id(region_id)
        if not region:
            return Response({'error': 'Region not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RegionDetailSerializer(region)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error getting region {region_id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_regions(request):
    """
    List regions
    
    GET /api/v1/regions/?world_id={world_id}
    """
    try:
        world_id = request.GET.get('world_id')
        active_only = request.GET.get('active_only', 'true').lower() == 'true'
        regions = RegionCRUDService.list_regions(world_id=world_id, active_only=active_only)
        
        serializer = RegionListSerializer(regions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error listing regions: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_region(request, region_id):
    """
    Update region
    
    PUT/PATCH /api/v1/regions/{region_id}/
    """
    try:
        serializer = RegionUpdateSerializer(data=request.data)
        if serializer.is_valid():
            region = RegionCRUDService.update_region(region_id, serializer.validated_data)
            if not region:
                return Response({'error': 'Region not found'}, status=status.HTTP_404_NOT_FOUND)
            
            response_serializer = RegionDetailSerializer(region)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error updating region {region_id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_region(request, region_id):
    """
    Delete region
    
    DELETE /api/v1/regions/{region_id}/
    """
    try:
        hard_delete = request.GET.get('hard_delete', 'false').lower() == 'true'
        success = RegionCRUDService.delete_region(region_id, hard_delete=hard_delete)
        
        if success:
            return Response({'message': 'Region deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Region not found'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f"Error deleting region {region_id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_regions(request):
    """
    Search regions
    
    GET /api/v1/regions/search/?q={query}&world_id={world_id}
    """
    try:
        query = request.GET.get('q', '')
        world_id = request.GET.get('world_id')
        
        if not query:
            return Response({'error': 'Query parameter "q" is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        regions = RegionCRUDService.search_regions(query, world_id=world_id)
        serializer = RegionListSerializer(regions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error searching regions: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_region_statistics(request, region_id):
    """
    Get region statistics
    
    GET /api/v1/regions/{region_id}/statistics/
    """
    try:
        stats = RegionCRUDService.get_region_statistics(region_id)
        if not stats:
            return Response({'error': 'Region not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RegionStatisticsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error getting region statistics {region_id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 