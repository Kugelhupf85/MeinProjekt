"""
User Serializers for Core User API.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from ...models import User, SecurityQuestion, UserSecurityAnswer


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with email verification.
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 
            'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        """
        Validate that passwords match.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        """
        Create user with email verification token.
        """
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        user.generate_email_verification_token()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.
    """
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'full_name', 'avatar', 'is_email_verified',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'email', 'is_email_verified', 'date_joined', 'last_login']


class SecurityQuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for security questions.
    """
    class Meta:
        model = SecurityQuestion
        fields = ['id', 'question_text']


class UserSecurityAnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for user security answers.
    """
    question = SecurityQuestionSerializer(read_only=True)
    question_id = serializers.IntegerField(write_only=True)
    answer = serializers.CharField(write_only=True)
    
    class Meta:
        model = UserSecurityAnswer
        fields = ['id', 'question', 'question_id', 'answer', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        """
        Create security answer with hashed storage.
        """
        answer = validated_data.pop('answer')
        question_id = validated_data.pop('question_id')
        
        security_answer = UserSecurityAnswer.objects.create(
            user=self.context['request'].user,
            question_id=question_id
        )
        security_answer.set_answer(answer)
        return security_answer


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification.
    """
    token = serializers.CharField()
    
    def validate_token(self, value):
        """
        Validate the verification token.
        """
        user = self.context['user']
        if not user.verify_email(value):
            raise serializers.ValidationError("Invalid verification token")
        return value 