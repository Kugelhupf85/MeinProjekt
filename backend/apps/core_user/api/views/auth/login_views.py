"""
Login Views for Authentication with JWT.
"""
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.utils.translation import gettext_lazy as _
from ...serializers.auth import LoginSerializer, LogoutSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    User login with email/username and password.
    Returns JWT tokens for authentication.
    
    POST /api/auth/login/
    {
        "username": "user@example.com",
        "password": "password123"
    }
    
    Response:
    {
        "message": "Login successful",
        "user": {...},
        "tokens": {
            "access": "jwt_access_token",
            "refresh": "jwt_refresh_token"
        }
    }
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data['user']
    
    # Create JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    
    # Also create session for backward compatibility
    login(request, user)
    
    return Response({
        'message': _('Login successful'),
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'is_email_verified': user.is_email_verified
        },
        'tokens': {
            'access': str(access_token),
            'refresh': str(refresh)
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    User logout.
    Blacklists the refresh token if provided.
    
    POST /api/auth/logout/
    {
        "refresh": "jwt_refresh_token"  // optional
    }
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except Exception:
        # Token might be invalid or already blacklisted
        pass
    
    # Also logout session
    logout(request)
    
    return Response({
        'message': _('Logout successful')
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_auth_view(request):
    """
    Check if user is authenticated.
    Works with both JWT and session authentication.
    
    GET /api/auth/check/
    Headers: Authorization: Bearer <jwt_access_token>
    """
    return Response({
        'authenticated': True,
        'user': {
            'id': request.user.id,
            'email': request.user.email,
            'full_name': request.user.full_name,
            'is_email_verified': request.user.is_email_verified
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def refresh_token_view(request):
    """
    Refresh JWT access token.
    
    POST /api/auth/refresh/
    {
        "refresh": "jwt_refresh_token"
    }
    
    Response:
    {
        "access": "new_jwt_access_token"
    }
    """
    from rest_framework_simplejwt.views import TokenRefreshView
    from rest_framework_simplejwt.serializers import TokenRefreshSerializer
    
    serializer = TokenRefreshSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    return Response(serializer.validated_data, status=status.HTTP_200_OK) 