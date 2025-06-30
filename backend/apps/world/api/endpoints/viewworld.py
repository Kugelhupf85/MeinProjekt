"""
World API Views
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from apps.world.services.crudworld import WorldCRUDService
from apps.world.api.serializers.serializerworld import (
    WorldCreateSerializer, WorldUpdateSerializer, WorldDetailSerializer,
    WorldListSerializer, WorldStatisticsSerializer
)
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_world(request):
    """
    Create a new world
    
    POST /api/v1/worlds/
    """
    try:
        serializer = WorldCreateSerializer(data=request.data)
        if serializer.is_valid():
            world = WorldCRUDService.create_world(serializer.validated_data)
            response_serializer = WorldDetailSerializer(world)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating world: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_world(request, world_id):
    """
    Get world by ID
    
    GET /api/v1/worlds/{world_id}/
    """
    try:
        world = WorldCRUDService.get_world_by_id(world_id)
        if not world:
            return Response({'error': 'World not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = WorldDetailSerializer(world)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error getting world {world_id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_worlds(request):
    """
    List all worlds
    
    GET /api/v1/worlds/
    """
    try:
        active_only = request.GET.get('active_only', 'true').lower() == 'true'
        worlds = WorldCRUDService.list_worlds(active_only=active_only)
        
        serializer = WorldListSerializer(worlds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error listing worlds: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_world(request, world_id):
    """
    Update world
    
    PUT/PATCH /api/v1/worlds/{world_id}/
    """
    try:
        serializer = WorldUpdateSerializer(data=request.data)
        if serializer.is_valid():
            world = WorldCRUDService.update_world(world_id, serializer.validated_data)
            if not world:
                return Response({'error': 'World not found'}, status=status.HTTP_404_NOT_FOUND)
            
            response_serializer = WorldDetailSerializer(world)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error updating world {world_id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_world(request, world_id):
    """
    Delete world
    
    DELETE /api/v1/worlds/{world_id}/
    """
    try:
        hard_delete = request.GET.get('hard_delete', 'false').lower() == 'true'
        success = WorldCRUDService.delete_world(world_id, hard_delete=hard_delete)
        
        if success:
            return Response({'message': 'World deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'World not found'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f"Error deleting world {world_id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_worlds(request):
    """
    Search worlds
    
    GET /api/v1/worlds/search/?q={query}
    """
    try:
        query = request.GET.get('q', '')
        if not query:
            return Response({'error': 'Query parameter "q" is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        worlds = WorldCRUDService.search_worlds(query)
        serializer = WorldListSerializer(worlds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error searching worlds: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_world_statistics(request, world_id):
    """
    Get world statistics
    
    GET /api/v1/worlds/{world_id}/statistics/
    """
    try:
        stats = WorldCRUDService.get_world_statistics(world_id)
        if not stats:
            return Response({'error': 'World not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = WorldStatisticsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error getting world statistics {world_id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 