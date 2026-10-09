"""
Security Question Views.
"""
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from ....models import SecurityQuestion, UserSecurityAnswer
from ...serializers.security import (
    SecurityQuestionSerializer,
    UserSecurityAnswerSerializer,
    SecurityAnswerBulkCreateSerializer,
    SecurityQuestionManagementSerializer
)


class SecurityQuestionListView(generics.ListAPIView):
    """
    List all active security questions.
    
    GET /api/auth/security-questions/
    """
    queryset = SecurityQuestion.objects.filter(is_active=True).order_by('question_text')
    serializer_class = SecurityQuestionSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_security_answers_view(request):
    """
    Get current user's security answers (without revealing answers).
    
    GET /api/auth/my-security-answers/
    """
    answers = request.user.security_answers.select_related('question').all()
    serializer = UserSecurityAnswerSerializer(answers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def set_security_answers_view(request):
    """
    Set security answers for the current user.
    
    POST /api/auth/set-security-answers/
    {
        "answers": [
            {"question_id": 1, "answer": "Gandalf"},
            {"question_id": 3, "answer": "D&D 5e"},
            {"question_id": 5, "answer": "Wizard"}
        ]
    }
    """
    serializer = SecurityAnswerBulkCreateSerializer(
        data=request.data,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    created_answers = serializer.save()
    
    return Response({
        'message': _(f'{len(created_answers)} security answers set successfully'),
        'count': len(created_answers)
    }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_security_answers_view(request):
    """
    Clear all security answers for the current user.
    
    DELETE /api/auth/clear-security-answers/
    """
    count = request.user.security_answers.count()
    request.user.security_answers.all().delete()
    
    return Response({
        'message': _(f'{count} security answers cleared successfully'),
        'count': count
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_user_security_questions_view(request):
    """
    Get security questions for a specific user (for password reset).
    
    GET /api/auth/user-security-questions/?email=user@example.com
    """
    email = request.query_params.get('email')
    if not email:
        return Response({
            'error': _('Email parameter is required')
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from ....models import User
        user = User.objects.get(email=email, is_active=True)
        answers = user.security_answers.select_related('question').all()
        
        if answers.count() < 2:
            return Response({
                'error': _('This account does not have enough security questions set up')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Return only the questions, not the answers
        questions = [answer.question for answer in answers]
        serializer = SecurityQuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': _('Account not found')
        }, status=status.HTTP_404_NOT_FOUND)


# Admin views
class SecurityQuestionManagementView(generics.ListCreateAPIView):
    """
    Manage security questions (admin only).
    
    GET /api/auth/admin/security-questions/
    POST /api/auth/admin/security-questions/
    """
    queryset = SecurityQuestion.objects.all().order_by('question_text')
    serializer_class = SecurityQuestionManagementSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def toggle_security_question_view(request, question_id):
    """
    Toggle security question active status (admin only).
    
    PATCH /api/auth/admin/security-questions/{question_id}/toggle/
    """
    try:
        question = SecurityQuestion.objects.get(id=question_id)
        question.is_active = not question.is_active
        question.save()
        
        return Response({
            'message': _('Security question status updated successfully'),
            'is_active': question.is_active
        }, status=status.HTTP_200_OK)
    except SecurityQuestion.DoesNotExist:
        return Response({
            'error': _('Security question not found')
        }, status=status.HTTP_404_NOT_FOUND) 