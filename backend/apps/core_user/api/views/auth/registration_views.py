"""
Registration Views for User Creation.
"""
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from ...serializers.auth import UserRegistrationSerializer, EmailVerificationSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """
    User registration.
    
    POST /api/auth/register/
    {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "password123",
        "password_confirm": "password123"
    }
    """
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    
    return Response({
        'message': _('User registered successfully. Please verify your email.'),
        'user_id': user.id,
        'email': user.email,
        'verification_token': user.email_verification_token
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_email_view(request):
    """
    Verify user email with token.
    
    POST /api/auth/verify-email/
    {
        "token": "verification-token-here"
    }
    """
    serializer = EmailVerificationSerializer(
        data=request.data,
        context={'user': request.user}
    )
    serializer.is_valid(raise_exception=True)
    
    return Response({
        'message': _('Email verified successfully')
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resend_verification_view(request):
    """
    Resend email verification token.
    
    POST /api/auth/resend-verification/
    """
    user = request.user
    
    if user.is_email_verified:
        return Response({
            'message': _('Email is already verified')
        }, status=status.HTTP_400_BAD_REQUEST)
    
    token = user.generate_email_verification_token()
    
    return Response({
        'message': _('Verification email sent'),
        'verification_token': token
    }, status=status.HTTP_200_OK) 