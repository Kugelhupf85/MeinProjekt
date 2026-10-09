"""
User Views for Core User API.
"""
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from ...models import User, SecurityQuestion
from ..serializers.user_serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    SecurityQuestionSerializer,
    UserSecurityAnswerSerializer,
    EmailVerificationSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management.
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    
    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserProfileSerializer
    
    def create(self, request):
        """
        Register a new user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'User registered successfully. Please verify your email.',
            'user_id': user.id,
            'verification_token': user.email_verification_token
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        Get current user profile.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """
        Update current user profile.
        """
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        """
        Verify user email with token.
        """
        serializer = EmailVerificationSerializer(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        
        return Response({
            'message': 'Email verified successfully'
        })
    
    @action(detail=False, methods=['get'])
    def security_questions(self, request):
        """
        Get available security questions.
        """
        questions = SecurityQuestion.objects.filter(is_active=True)
        serializer = SecurityQuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def set_security_answers(self, request):
        """
        Set security answers for the user.
        """
        if not isinstance(request.data, list):
            return Response({
                'error': 'Expected a list of security answers'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(request.data) < 2:
            return Response({
                'error': 'At least 2 security questions are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete existing answers
        request.user.security_answers.all().delete()
        
        # Create new answers
        created_answers = []
        for answer_data in request.data:
            serializer = UserSecurityAnswerSerializer(
                data=answer_data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            created_answers.append(serializer.save())
        
        return Response({
            'message': f'{len(created_answers)} security answers set successfully'
        }, status=status.HTTP_201_CREATED) 