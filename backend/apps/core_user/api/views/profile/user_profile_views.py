"""
User Profile Views.
"""
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from ....models import User
from ...serializers.profile import (
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserListSerializer
)
from django.db import models


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """
    Get current user profile.
    
    GET /api/auth/profile/
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile_view(request):
    """
    Update current user profile.
    
    PUT/PATCH /api/auth/profile/update/
    {
        "first_name": "John",
        "last_name": "Doe",
        "avatar": file_upload
    }
    """
    serializer = UserProfileUpdateSerializer(
        request.user,
        data=request.data,
        partial=request.method == 'PATCH'
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    # Return updated profile
    profile_serializer = UserProfileSerializer(request.user)
    return Response({
        'message': _('Profile updated successfully'),
        'user': profile_serializer.data
    }, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """
    List all users (admin only).
    
    GET /api/auth/users/
    """
    queryset = User.objects.filter(is_active=True).order_by('-date_joined')
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """
        Optionally filter users by search query.
        """
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )
        
        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def user_detail_view(request, user_id):
    """
    Get specific user details (admin only).
    
    GET /api/auth/users/{user_id}/
    """
    try:
        user = User.objects.get(id=user_id)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({
            'error': _('User not found')
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def toggle_user_active_view(request, user_id):
    """
    Toggle user active status (admin only).
    
    PATCH /api/auth/users/{user_id}/toggle-active/
    """
    try:
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        
        return Response({
            'message': _('User status updated successfully'),
            'is_active': user.is_active
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({
            'error': _('User not found')
        }, status=status.HTTP_404_NOT_FOUND) 