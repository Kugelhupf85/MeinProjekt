"""
Views for DungeonMaster model API.
"""
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404

from ...models import DungeonMaster, UserSettings, UserKeys
from ..serializers import (
    DungeonMasterOutputSerializer,
    DungeonMasterCreateSerializer,
    DungeonMasterUpdateSerializer,
    DungeonMasterListSerializer,
    DungeonMasterPublicSerializer,
    UserUpdateSerializer,
)


class DungeonMasterViewSet(ModelViewSet):
    """
    ViewSet for DungeonMaster CRUD operations.
    
    Provides:
    - list: GET /api/dungeon-masters/
    - create: POST /api/dungeon-masters/
    - retrieve: GET /api/dungeon-masters/{id}/
    - update: PUT /api/dungeon-masters/{id}/
    - partial_update: PATCH /api/dungeon-masters/{id}/
    - destroy: DELETE /api/dungeon-masters/{id}/
    - profile: GET /api/dungeon-masters/profile/ (current user's profile)
    - update_user: PATCH /api/dungeon-masters/{id}/update-user/
    - public_profiles: GET /api/dungeon-masters/public/
    """
    
    queryset = DungeonMaster.objects.select_related('user').all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action.
        """
        if self.action == 'create':
            return DungeonMasterCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DungeonMasterUpdateSerializer
        elif self.action == 'list':
            return DungeonMasterListSerializer
        elif self.action == 'public_profiles':
            return DungeonMasterPublicSerializer
        elif self.action == 'update_user':
            return UserUpdateSerializer
        else:
            return DungeonMasterOutputSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on action and user permissions.
        """
        queryset = super().get_queryset()
        
        if self.action == 'public_profiles':
            return queryset.filter(is_public=True, is_active=True)
        
        # For authenticated users, return all active profiles
        return queryset.filter(is_active=True)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new DungeonMaster profile with associated User.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # Create User
            user_data = {
                'username': serializer.validated_data['username'],
                'email': serializer.validated_data['email'],
                'first_name': serializer.validated_data.get('first_name', ''),
                'last_name': serializer.validated_data.get('last_name', ''),
            }
            user = User.objects.create_user(
                password=serializer.validated_data['password'],
                **user_data
            )
            
            # Create DungeonMaster
            dm_data = {k: v for k, v in serializer.validated_data.items() 
                      if k not in ['username', 'email', 'password', 'first_name', 'last_name']}
            dm_data['user'] = user
            
            dungeon_master = DungeonMaster.objects.create(**dm_data)
            
            # Create associated UserSettings and UserKeys
            UserSettings.objects.create(dungeonmaster=dungeon_master)
            UserKeys.objects.create(dungeonmaster=dungeon_master)
        
        output_serializer = DungeonMasterOutputSerializer(dungeon_master)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        Update DungeonMaster profile.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Update DungeonMaster fields
        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        output_serializer = DungeonMasterOutputSerializer(instance)
        return Response(output_serializer.data)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        Get the current user's DungeonMaster profile.
        """
        try:
            dungeon_master = DungeonMaster.objects.select_related('user').get(
                user=request.user
            )
            serializer = DungeonMasterOutputSerializer(dungeon_master)
            return Response(serializer.data)
        except DungeonMaster.DoesNotExist:
            return Response(
                {'detail': 'DungeonMaster profile not found for current user.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['patch'])
    def update_user(self, request, pk=None):
        """
        Update the User information associated with a DungeonMaster.
        """
        dungeon_master = self.get_object()
        user = dungeon_master.user
        
        serializer = UserUpdateSerializer(
            user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Update User fields
        for attr, value in serializer.validated_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Return updated DungeonMaster profile
        output_serializer = DungeonMasterOutputSerializer(dungeon_master)
        return Response(output_serializer.data)
    
    @action(detail=False, methods=['get'])
    def public_profiles(self, request):
        """
        Get public DungeonMaster profiles.
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_public(self, request, pk=None):
        """
        Toggle the public visibility of a DungeonMaster profile.
        """
        dungeon_master = self.get_object()
        dungeon_master.is_public = not dungeon_master.is_public
        dungeon_master.save()
        
        serializer = DungeonMasterOutputSerializer(dungeon_master)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_green_flag(self, request, pk=None):
        """
        Add a green flag (positive preference) to the profile.
        """
        dungeon_master = self.get_object()
        flag = request.data.get('flag')
        
        if not flag:
            return Response(
                {'detail': 'Flag is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dungeon_master.add_green_flag(flag)
        serializer = DungeonMasterOutputSerializer(dungeon_master)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def remove_green_flag(self, request, pk=None):
        """
        Remove a green flag from the profile.
        """
        dungeon_master = self.get_object()
        flag = request.data.get('flag')
        
        if not flag:
            return Response(
                {'detail': 'Flag is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dungeon_master.remove_green_flag(flag)
        serializer = DungeonMasterOutputSerializer(dungeon_master)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_red_flag(self, request, pk=None):
        """
        Add a red flag (negative preference) to the profile.
        """
        dungeon_master = self.get_object()
        flag = request.data.get('flag')
        
        if not flag:
            return Response(
                {'detail': 'Flag is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dungeon_master.add_red_flag(flag)
        serializer = DungeonMasterOutputSerializer(dungeon_master)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def remove_red_flag(self, request, pk=None):
        """
        Remove a red flag from the profile.
        """
        dungeon_master = self.get_object()
        flag = request.data.get('flag')
        
        if not flag:
            return Response(
                {'detail': 'Flag is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dungeon_master.remove_red_flag(flag)
        serializer = DungeonMasterOutputSerializer(dungeon_master)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_theme_preference(self, request, pk=None):
        """
        Add a theme preference to the profile.
        """
        dungeon_master = self.get_object()
        theme = request.data.get('theme')
        
        if not theme:
            return Response(
                {'detail': 'Theme is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dungeon_master.add_theme_preference(theme)
        serializer = DungeonMasterOutputSerializer(dungeon_master)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def remove_theme_preference(self, request, pk=None):
        """
        Remove a theme preference from the profile.
        """
        dungeon_master = self.get_object()
        theme = request.data.get('theme')
        
        if not theme:
            return Response(
                {'detail': 'Theme is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dungeon_master.remove_theme_preference(theme)
        serializer = DungeonMasterOutputSerializer(dungeon_master)
        return Response(serializer.data) 