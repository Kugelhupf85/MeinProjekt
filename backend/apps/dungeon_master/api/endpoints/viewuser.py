"""
API endpoints for Dungeon Master user management.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from typing import Dict, Any

from ..serializers import (
    DungeonMasterCreateSerializer,
    DungeonMasterOutputSerializer,
    DungeonMasterUpdateSerializer,
    DungeonMasterListSerializer,
    UserUpdateSerializer,
    SettingUpdateSerializer,
)
from ...services.cruduser import DungeonMasterCRUD
from ...models import DungeonMaster


@api_view(['POST'])
@permission_classes([AllowAny])
def create_dungeon_master(request: Request) -> Response:
    """
    Create a new DungeonMaster account.
    
    POST /api/dungeon-master/create/
    """
    serializer = DungeonMasterCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {"error": "Validation failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Extract validated data
        validated_data = serializer.validated_data
        
        # Create DungeonMaster using service
        dungeon_master = DungeonMasterCRUD.create_dungeon_master(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            game_system_setting=validated_data.get('game_system_setting', {}),
            ui_settings=validated_data.get('ui_settings', {}),
            ai_settings=validated_data.get('ai_settings', {})
        )
        
        # Serialize response
        output_serializer = DungeonMasterOutputSerializer(dungeon_master)
        
        return Response(
            {
                "message": "DungeonMaster created successfully",
                "data": output_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
        
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dungeon_master_profile(request: Request, entity_id: str) -> Response:
    """
    Get DungeonMaster profile by entity_id.
    
    GET /api/dungeon-master/{entity_id}/
    """
    dungeon_master = DungeonMasterCRUD.get_dungeon_master_by_entity_id(entity_id)
    
    if not dungeon_master:
        return Response(
            {"error": f"DungeonMaster with entity_id '{entity_id}' not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions - user can only access their own profile
    if request.user != dungeon_master.user:
        return Response(
            {"error": "Permission denied"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = DungeonMasterOutputSerializer(dungeon_master)
    
    return Response(
        {
            "message": "DungeonMaster profile retrieved successfully",
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_dungeon_masters(request: Request) -> Response:
    """
    List DungeonMasters with optional filtering and pagination.
    
    GET /api/dungeon-master/list/
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - search: Search term for username/email/name
    """
    try:
        # Parse query parameters
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        search = request.GET.get('search', '').strip()
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get DungeonMasters using service
        dungeon_masters = DungeonMasterCRUD.list_dungeon_masters(
            limit=page_size,
            offset=offset,
            search=search if search else None,
            active_only=True
        )
        
        # Get total count for pagination
        total_count = DungeonMasterCRUD.get_dungeon_master_count()
        
        # Serialize response
        serializer = DungeonMasterListSerializer(dungeon_masters, many=True)
        
        return Response(
            {
                "message": "DungeonMasters retrieved successfully",
                "data": serializer.data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size
                }
            },
            status=status.HTTP_200_OK
        )
        
    except ValueError as e:
        return Response(
            {"error": f"Invalid parameters: {e}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_dungeon_master_profile(request: Request, entity_id: str) -> Response:
    """
    Update DungeonMaster profile settings.
    
    PUT /api/dungeon-master/{entity_id}/profile/
    """
    dungeon_master = DungeonMasterCRUD.get_dungeon_master_by_entity_id(entity_id)
    
    if not dungeon_master:
        return Response(
            {"error": f"DungeonMaster with entity_id '{entity_id}' not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions
    if request.user != dungeon_master.user:
        return Response(
            {"error": "Permission denied"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = DungeonMasterUpdateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {"error": "Validation failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        validated_data = serializer.validated_data
        
        # Update profile using service
        updated_dm = DungeonMasterCRUD.update_dungeon_master_profile(
            entity_id=entity_id,
            game_system_setting=validated_data.get('game_system_setting'),
            ui_settings=validated_data.get('ui_settings'),
            ai_settings=validated_data.get('ai_settings')
        )
        
        # Serialize response
        output_serializer = DungeonMasterOutputSerializer(updated_dm)
        
        return Response(
            {
                "message": "DungeonMaster profile updated successfully",
                "data": output_serializer.data
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_info(request: Request, entity_id: str) -> Response:
    """
    Update User information for a DungeonMaster.
    
    PUT /api/dungeon-master/{entity_id}/user/
    """
    dungeon_master = DungeonMasterCRUD.get_dungeon_master_by_entity_id(entity_id)
    
    if not dungeon_master:
        return Response(
            {"error": f"DungeonMaster with entity_id '{entity_id}' not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions
    if request.user != dungeon_master.user:
        return Response(
            {"error": "Permission denied"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = UserUpdateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {"error": "Validation failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        validated_data = serializer.validated_data
        
        # Update user info using service
        updated_dm = DungeonMasterCRUD.update_user_info(
            entity_id=entity_id,
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            email=validated_data.get('email')
        )
        
        # Serialize response
        output_serializer = DungeonMasterOutputSerializer(updated_dm)
        
        return Response(
            {
                "message": "User information updated successfully",
                "data": output_serializer.data
            },
            status=status.HTTP_200_OK
        )
        
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_individual_setting(request: Request, entity_id: str) -> Response:
    """
    Update an individual setting in one of the JSON fields.
    
    PUT /api/dungeon-master/{entity_id}/setting/
    """
    dungeon_master = DungeonMasterCRUD.get_dungeon_master_by_entity_id(entity_id)
    
    if not dungeon_master:
        return Response(
            {"error": f"DungeonMaster with entity_id '{entity_id}' not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions
    if request.user != dungeon_master.user:
        return Response(
            {"error": "Permission denied"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = SettingUpdateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {"error": "Validation failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        validated_data = serializer.validated_data
        
        # Update setting using service
        updated_dm = DungeonMasterCRUD.update_individual_setting(
            entity_id=entity_id,
            setting_type=validated_data['setting_type'],
            key=validated_data['key'],
            value=validated_data['value']
        )
        
        # Serialize response
        output_serializer = DungeonMasterOutputSerializer(updated_dm)
        
        return Response(
            {
                "message": "Setting updated successfully",
                "data": output_serializer.data
            },
            status=status.HTTP_200_OK
        )
        
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deactivate_dungeon_master(request: Request, entity_id: str) -> Response:
    """
    Soft delete a DungeonMaster account.
    
    DELETE /api/dungeon-master/{entity_id}/deactivate/
    """
    dungeon_master = DungeonMasterCRUD.get_dungeon_master_by_entity_id(entity_id)
    
    if not dungeon_master:
        return Response(
            {"error": f"DungeonMaster with entity_id '{entity_id}' not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions
    if request.user != dungeon_master.user:
        return Response(
            {"error": "Permission denied"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Deactivate using service
        success = DungeonMasterCRUD.deactivate_dungeon_master(entity_id)
        
        if success:
            return Response(
                {"message": "DungeonMaster account deactivated successfully"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Failed to deactivate account"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_dungeon_masters(request: Request) -> Response:
    """
    Search DungeonMasters by username, email, or name.
    
    GET /api/dungeon-master/search/
    Query parameters:
    - q: Search term (required)
    - limit: Maximum results (default: 20, max: 50)
    """
    search_term = request.GET.get('q', '').strip()
    
    if not search_term:
        return Response(
            {"error": "Search term 'q' is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        limit = min(int(request.GET.get('limit', 20)), 50)
        
        # Search using service
        dungeon_masters = DungeonMasterCRUD.search_dungeon_masters(
            search_term=search_term,
            limit=limit
        )
        
        # Serialize response
        serializer = DungeonMasterListSerializer(dungeon_masters, many=True)
        
        return Response(
            {
                "message": f"Found {len(dungeon_masters)} DungeonMasters",
                "data": serializer.data,
                "search_term": search_term
            },
            status=status.HTTP_200_OK
        )
        
    except ValueError as e:
        return Response(
            {"error": f"Invalid parameters: {e}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 