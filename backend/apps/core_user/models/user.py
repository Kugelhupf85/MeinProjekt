"""
Standard User Model for Arcanovi SaaS.
Replaces the previous ArcanoviUser with standardized SaaS user management.
"""
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom User Manager for Email-based Authentication.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_email_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Standard User Model for Arcanovi SaaS.
    
    Features:
    - Email as primary login (no username required)
    - Email verification system
    - Avatar support
    - Security questions for password reset
    - Standardized timestamps
    """
    
    # Remove username field - we use email instead
    username = None
    
    # Email as primary identifier
    email = models.EmailField(
        _('email address'),
        unique=True,
        validators=[EmailValidator()],
        help_text=_('Required. Enter a valid email address.')
    )
    
    # Email verification
    is_email_verified = models.BooleanField(
        default=False,
        help_text=_('Whether the user has verified their email address')
    )
    
    email_verification_token = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Token for email verification')
    )
    
    # User profile information
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text=_('User avatar image')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Timestamp when the user was created')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('Timestamp when the user was last updated')
    )
    
    # Use email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        db_table = 'core_user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        """
        String representation showing full name or email.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    @property
    def full_name(self):
        """
        Return the full name of the user.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email
    
    def generate_email_verification_token(self):
        """
        Generate a new email verification token.
        """
        self.email_verification_token = str(uuid.uuid4())
        self.save(update_fields=['email_verification_token'])
        return self.email_verification_token
    
    def verify_email(self, token):
        """
        Verify email with the provided token.
        """
        if self.email_verification_token == token:
            self.is_email_verified = True
            self.email_verification_token = None
            self.save(update_fields=['is_email_verified', 'email_verification_token'])
            return True
        return False 