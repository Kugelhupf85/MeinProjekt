"""
API endpoints for Adventure campaign management.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from typing import Dict, Any

from ...services.crudcampaign import AdventureCRUD
from ...models import Adventure
from apps.dungeon_master.models import DungeonMaster


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_adventure(request: Request) -> Response:
    """
    Create a new Adventure.
    
    POST /api/adventure/create/
    """
    try:
        # Get DungeonMaster for the authenticated user
        dm = DungeonMaster.objects.get(user=request.user, is_active=True)
        
        # Extract data from request
        data = request.data
        name = data.get('name')
        description = data.get('description', '')
        game_system = data.get('game_system', 'D&D 5e')
        adventure_settings = data.get('adventure_settings', {})
        world_building = data.get('world_building', {})
        player_count = data.get('player_count', 0)
        
        if not name:
            return Response(
                {"error": "Adventure name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create Adventure using service
        adventure = AdventureCRUD.create_adventure(
            dungeon_master_entity_id=dm.entity_id,
            name=name,
            description=description,
            game_system=game_system,
            adventure_settings=adventure_settings,
            world_building=world_building,
            player_count=player_count
        )
        
        return Response(
            {
                "message": "Adventure created successfully",
                "data": {
                    "entity_id": adventure.entity_id,
                    "name": adventure.name,
                    "description": adventure.description,
                    "game_system": adventure.game_system,
                    "status": adventure.status,
                    "player_count": adventure.player_count,
                    "created_at": adventure.created_at.isoformat()
                }
            },
            status=status.HTTP_201_CREATED
        )
        
    except DungeonMaster.DoesNotExist:
        return Response(
            {"error": "DungeonMaster profile not found for authenticated user"},
            status=status.HTTP_404_NOT_FOUND
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
def get_adventure(request: Request, entity_id: str) -> Response:
    """
    Get Adventure by entity_id.
    
    GET /api/adventure/{entity_id}/
    """
    adventure = AdventureCRUD.get_adventure_by_entity_id(entity_id)
    
    if not adventure:
        return Response(
            {"error": f"Adventure with entity_id '{entity_id}' not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions - only owner or public adventures
    try:
        dm = DungeonMaster.objects.get(user=request.user, is_active=True)
        if adventure.dungeon_master != dm and not adventure.is_public:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )
    except DungeonMaster.DoesNotExist:
        if not adventure.is_public:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )
    
    return Response(
        {
            "message": "Adventure retrieved successfully",
            "data": {
                "entity_id": adventure.entity_id,
                "name": adventure.name,
                "description": adventure.description,
                "game_system": adventure.game_system,
                "status": adventure.status,
                "player_count": adventure.player_count,
                "is_public": adventure.is_public,
                "adventure_settings": adventure.adventure_settings,
                "world_building": adventure.world_building,
                "session_notes": adventure.session_notes,
                "character_sheets": adventure.character_sheets,
                "campaign_timeline": adventure.campaign_timeline,
                "rules_modifications": adventure.rules_modifications,
                "current_session": adventure.current_session,
                "total_sessions": adventure.total_sessions,
                "created_at": adventure.created_at.isoformat(),
                "updated_at": adventure.updated_at.isoformat(),
                "started_at": adventure.started_at.isoformat() if adventure.started_at else None,
                "completed_at": adventure.completed_at.isoformat() if adventure.completed_at else None,
                "dungeon_master": {
                    "entity_id": adventure.dungeon_master.entity_id,
                    "username": adventure.dungeon_master.user.username
                }
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_my_adventures(request: Request) -> Response:
    """
    List Adventures for the authenticated DungeonMaster.
    
    GET /api/adventure/my/
    """
    try:
        # Get DungeonMaster for the authenticated user
        dm = DungeonMaster.objects.get(user=request.user, is_active=True)
        
        # Optional status filter
        status_filter = request.GET.get('status')
        
        # Get Adventures using service
        adventures = AdventureCRUD.list_adventures_by_dm(
            dungeon_master_entity_id=dm.entity_id,
            status_filter=status_filter
        )
        
        # Format response data
        adventure_data = []
        for adventure in adventures:
            adventure_data.append({
                "entity_id": adventure.entity_id,
                "name": adventure.name,
                "description": adventure.description,
                "game_system": adventure.game_system,
                "status": adventure.status,
                "player_count": adventure.player_count,
                "is_public": adventure.is_public,
                "current_session": adventure.current_session,
                "total_sessions": adventure.total_sessions,
                "created_at": adventure.created_at.isoformat(),
                "updated_at": adventure.updated_at.isoformat()
            })
        
        return Response(
            {
                "message": f"Found {len(adventures)} adventures",
                "data": adventure_data,
                "total_count": len(adventures)
            },
            status=status.HTTP_200_OK
        )
        
    except DungeonMaster.DoesNotExist:
        return Response(
            {"error": "DungeonMaster profile not found for authenticated user"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_public_adventures(request: Request) -> Response:
    """
    List public Adventures.
    
    GET /api/adventure/public/
    """
    try:
        # Parse query parameters
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        game_system_filter = request.GET.get('game_system')
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get Adventures using service
        adventures = AdventureCRUD.list_public_adventures(
            limit=page_size,
            offset=offset,
            game_system_filter=game_system_filter
        )
        
        # Format response data
        adventure_data = []
        for adventure in adventures:
            adventure_data.append({
                "entity_id": adventure.entity_id,
                "name": adventure.name,
                "description": adventure.description,
                "game_system": adventure.game_system,
                "status": adventure.status,
                "player_count": adventure.player_count,
                "current_session": adventure.current_session,
                "total_sessions": adventure.total_sessions,
                "created_at": adventure.created_at.isoformat(),
                "dungeon_master": {
                    "username": adventure.dungeon_master.user.username
                }
            })
        
        return Response(
            {
                "message": f"Found {len(adventures)} public adventures",
                "data": adventure_data,
                "pagination": {
                    "page": page,
                    "page_size": page_size
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
def update_adventure(request: Request, entity_id: str) -> Response:
    """
    Update Adventure basic information.
    
    PUT /api/adventure/{entity_id}/
    """
    adventure = AdventureCRUD.get_adventure_by_entity_id(entity_id)
    
    if not adventure:
        return Response(
            {"error": f"Adventure with entity_id '{entity_id}' not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions - only owner can update
    try:
        dm = DungeonMaster.objects.get(user=request.user, is_active=True)
        if adventure.dungeon_master != dm:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )
    except DungeonMaster.DoesNotExist:
        return Response(
            {"error": "DungeonMaster profile not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        data = request.data
        
        # Update using service
        updated_adventure = AdventureCRUD.update_adventure_basic_info(
            entity_id=entity_id,
            name=data.get('name'),
            description=data.get('description'),
            game_system=data.get('game_system'),
            player_count=data.get('player_count'),
            is_public=data.get('is_public')
        )
        
        return Response(
            {
                "message": "Adventure updated successfully",
                "data": {
                    "entity_id": updated_adventure.entity_id,
                    "name": updated_adventure.name,
                    "description": updated_adventure.description,
                    "game_system": updated_adventure.game_system,
                    "status": updated_adventure.status,
                    "player_count": updated_adventure.player_count,
                    "is_public": updated_adventure.is_public,
                    "updated_at": updated_adventure.updated_at.isoformat()
                }
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
def update_adventure_status(request: Request, entity_id: str) -> Response:
    """
    Update Adventure status.
    
    PUT /api/adventure/{entity_id}/status/
    """
    adventure = AdventureCRUD.get_adventure_by_entity_id(entity_id)
    
    if not adventure:
        return Response(
            {"error": f"Adventure with entity_id '{entity_id}' not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions
    try:
        dm = DungeonMaster.objects.get(user=request.user, is_active=True)
        if adventure.dungeon_master != dm:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )
    except DungeonMaster.DoesNotExist:
        return Response(
            {"error": "DungeonMaster profile not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    new_status = request.data.get('status')
    if not new_status:
        return Response(
            {"error": "Status is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        updated_adventure = AdventureCRUD.update_adventure_status(
            entity_id=entity_id,
            new_status=new_status
        )
        
        return Response(
            {
                "message": "Adventure status updated successfully",
                "data": {
                    "entity_id": updated_adventure.entity_id,
                    "status": updated_adventure.status,
                    "started_at": updated_adventure.started_at.isoformat() if updated_adventure.started_at else None,
                    "completed_at": updated_adventure.completed_at.isoformat() if updated_adventure.completed_at else None,
                    "updated_at": updated_adventure.updated_at.isoformat()
                }
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
def delete_adventure(request: Request, entity_id: str) -> Response:
    """
    Delete an Adventure.
    
    DELETE /api/adventure/{entity_id}/
    """
    adventure = AdventureCRUD.get_adventure_by_entity_id(entity_id)
    
    if not adventure:
        return Response(
            {"error": f"Adventure with entity_id '{entity_id}' not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions
    try:
        dm = DungeonMaster.objects.get(user=request.user, is_active=True)
        if adventure.dungeon_master != dm:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )
    except DungeonMaster.DoesNotExist:
        return Response(
            {"error": "DungeonMaster profile not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        success = AdventureCRUD.delete_adventure(entity_id)
        
        if success:
            return Response(
                {"message": "Adventure deleted successfully"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Failed to delete adventure"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 