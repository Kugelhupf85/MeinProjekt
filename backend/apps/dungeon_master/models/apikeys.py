"""
User API Keys model for encrypted storage of external API keys.
"""
from django.db import models
from django.utils import timezone
from .dungeonmaster import DungeonMaster


class UserKeys(models.Model):
    """
    User API Keys model for encrypted storage of external service API keys.
    
    This model stores:
    - Encrypted API keys for various AI services
    - Key status and validation information
    - Usage statistics and rate limiting data
    - Security metadata and encryption versioning
    """
    
    KEY_STATUS_CHOICES = [
        ('not_configured', 'Not Configured'),
        ('configured', 'Configured'),
        ('invalid', 'Invalid'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
    ]
    
    dungeonmaster = models.OneToOneField(
        DungeonMaster,
        on_delete=models.CASCADE,
        related_name='api_keys',
        help_text="Link to DungeonMaster profile"
    )
    
    # Encrypted API Keys (using pgcrypto extension)
    openai_key_encrypted = models.BinaryField(
        null=True,
        blank=True,
        help_text="Encrypted OpenAI API key"
    )
    
    anthropic_key_encrypted = models.BinaryField(
        null=True,
        blank=True,
        help_text="Encrypted Anthropic API key"
    )
    
    google_key_encrypted = models.BinaryField(
        null=True,
        blank=True,
        help_text="Encrypted Google API key"
    )
    
    deepseek_key_encrypted = models.BinaryField(
        null=True,
        blank=True,
        help_text="Encrypted DeepSeek API key"
    )
    
    # Key Status and Metadata
    openai_status = models.CharField(
        max_length=20,
        choices=KEY_STATUS_CHOICES,
        default='not_configured',
        help_text="Status of the OpenAI API key"
    )
    
    anthropic_status = models.CharField(
        max_length=20,
        choices=KEY_STATUS_CHOICES,
        default='not_configured',
        help_text="Status of the Anthropic API key"
    )
    
    google_status = models.CharField(
        max_length=20,
        choices=KEY_STATUS_CHOICES,
        default='not_configured',
        help_text="Status of the Google API key"
    )
    
    deepseek_status = models.CharField(
        max_length=20,
        choices=KEY_STATUS_CHOICES,
        default='not_configured',
        help_text="Status of the DeepSeek API key"
    )
    
    # Last Validation Timestamps
    openai_last_validated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when OpenAI key was last validated"
    )
    
    anthropic_last_validated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when Anthropic key was last validated"
    )
    
    google_last_validated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when Google key was last validated"
    )
    
    deepseek_last_validated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when DeepSeek key was last validated"
    )
    
    # Usage Tracking (for rate limiting and monitoring)
    usage_statistics = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON data for usage statistics and rate limiting"
    )
    
    # Security Metadata
    encryption_version = models.IntegerField(
        default=1,
        help_text="Version number for key rotation and encryption method"
    )
    
    last_key_update = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when any key was last updated"
    )
    
    security_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Admin notes about key issues or security concerns"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the API keys record was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the API keys record was last updated"
    )
    
    class Meta:
        db_table = 'dm_user_keys'
        verbose_name = 'User API Keys'
        verbose_name_plural = 'User API Keys'
        ordering = ['-updated_at']
    
    def __str__(self) -> str:
        """
        String representation showing the associated dungeon master.
        """
        return f"API Keys for {self.dungeonmaster}"
    
    @classmethod
    def get_default_usage_statistics(cls):
        """Return default usage statistics structure."""
        return {
            "openai": {"requests_today": 0, "last_request": None},
            "anthropic": {"requests_today": 0, "last_request": None},
            "google": {"requests_today": 0, "last_request": None},
            "deepseek": {"requests_today": 0, "last_request": None}
        }
    
    def save(self, *args, **kwargs):
        """
        Override save to set default values if not present.
        """
        if not self.usage_statistics:
            self.usage_statistics = self.get_default_usage_statistics()
        super().save(*args, **kwargs)
    
    def get_key_status(self, provider: str) -> str:
        """
        Get the status of a specific API key provider.
        
        Args:
            provider: The provider name ('openai', 'anthropic', 'google', 'deepseek')
            
        Returns:
            The status string or 'not_configured' if provider not found
        """
        status_field = f"{provider}_status"
        return getattr(self, status_field, 'not_configured')
    
    def set_key_status(self, provider: str, status: str):
        """
        Set the status of a specific API key provider.
        
        Args:
            provider: The provider name ('openai', 'anthropic', 'google', 'deepseek')
            status: The status to set
        """
        if status in dict(self.KEY_STATUS_CHOICES):
            status_field = f"{provider}_status"
            if hasattr(self, status_field):
                setattr(self, status_field, status)
                self.save()
    
    def get_last_validated(self, provider: str):
        """
        Get the last validation timestamp for a specific provider.
        
        Args:
            provider: The provider name ('openai', 'anthropic', 'google', 'deepseek')
            
        Returns:
            The last validation timestamp or None
        """
        validated_field = f"{provider}_last_validated"
        return getattr(self, validated_field, None)
    
    def set_last_validated(self, provider: str, timestamp=None):
        """
        Set the last validation timestamp for a specific provider.
        
        Args:
            provider: The provider name ('openai', 'anthropic', 'google', 'deepseek')
            timestamp: The timestamp to set (defaults to now)
        """
        if timestamp is None:
            timestamp = timezone.now()
        
        validated_field = f"{provider}_last_validated"
        if hasattr(self, validated_field):
            setattr(self, validated_field, timestamp)
            self.save()
    
    def has_encrypted_key(self, provider: str) -> bool:
        """
        Check if a provider has an encrypted key stored.
        
        Args:
            provider: The provider name ('openai', 'anthropic', 'google', 'deepseek')
            
        Returns:
            True if encrypted key exists, False otherwise
        """
        key_field = f"{provider}_key_encrypted"
        encrypted_key = getattr(self, key_field, None)
        return encrypted_key is not None and len(encrypted_key) > 0
    
    def get_usage_stats(self, provider: str) -> dict:
        """
        Get usage statistics for a specific provider.
        
        Args:
            provider: The provider name ('openai', 'anthropic', 'google', 'deepseek')
            
        Returns:
            Dictionary with usage statistics
        """
        return self.usage_statistics.get(provider, {"requests_today": 0, "last_request": None})
    
    def increment_usage(self, provider: str):
        """
        Increment the usage counter for a specific provider.
        
        Args:
            provider: The provider name ('openai', 'anthropic', 'google', 'deepseek')
        """
        if provider not in self.usage_statistics:
            self.usage_statistics[provider] = {"requests_today": 0, "last_request": None}
        
        self.usage_statistics[provider]["requests_today"] += 1
        self.usage_statistics[provider]["last_request"] = timezone.now().isoformat()
        self.save()
    
    def reset_daily_usage(self, provider: str = None):
        """
        Reset daily usage counters.
        
        Args:
            provider: Specific provider to reset, or None to reset all
        """
        if provider:
            if provider in self.usage_statistics:
                self.usage_statistics[provider]["requests_today"] = 0
        else:
            for p in ["openai", "anthropic", "google", "deepseek"]:
                if p in self.usage_statistics:
                    self.usage_statistics[p]["requests_today"] = 0
        self.save()
    
    def get_configured_providers(self) -> list:
        """
        Get a list of providers that have configured (non-empty) API keys.
        
        Returns:
            List of provider names with configured keys
        """
        providers = []
        for provider in ["openai", "anthropic", "google", "deepseek"]:
            if (self.has_encrypted_key(provider) and 
                self.get_key_status(provider) in ['configured', 'invalid', 'expired']):
                providers.append(provider)
        return providers 