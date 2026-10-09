"""
Password Management Views.
"""
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from ...serializers.auth import (
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetWithSecuritySerializer
)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    """
    Change user password (requires current password).
    
    POST /api/auth/change-password/
    {
        "current_password": "oldpassword",
        "new_password": "newpassword123",
        "new_password_confirm": "newpassword123"
    }
    """
    serializer = PasswordChangeSerializer(
        data=request.data,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    return Response({
        'message': _('Password changed successfully')
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password_request_view(request):
    """
    Request password reset via email.
    
    POST /api/auth/reset-password-request/
    {
        "email": "user@example.com"
    }
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Always return success to prevent email enumeration
    return Response({
        'message': _('If the email exists, a password reset link has been sent')
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password_with_security_view(request):
    """
    Reset password using security questions.
    
    POST /api/auth/reset-password-security/
    {
        "email": "user@example.com",
        "security_answers": [
            {"question_id": 1, "answer": "Gandalf"},
            {"question_id": 3, "answer": "D&D 5e"}
        ],
        "new_password": "newpassword123",
        "new_password_confirm": "newpassword123"
    }
    """
    serializer = PasswordResetWithSecuritySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    return Response({
        'message': _('Password reset successfully')
    }, status=status.HTTP_200_OK) 