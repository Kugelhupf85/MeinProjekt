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
        help_text="Last time the OpenAI key was validated"
    )
    
    anthropic_last_validated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time the Anthropic key was validated"
    )
    
    google_last_validated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time the Google key was validated"
    )
    
    deepseek_last_validated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time the DeepSeek key was validated"
    )
    
    # Usage Tracking (for rate limiting and monitoring)
    usage_statistics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Usage statistics for rate limiting and monitoring"
    )
    
    # Security Metadata
    encryption_version = models.IntegerField(
        default=1,
        help_text="Encryption version for key rotation"
    )
    
    last_key_update = models.DateTimeField(
        default=timezone.now,
        help_text="Last time any key was updated"
    )
    
    security_notes = models.TextField(
        blank=True,
        help_text="Admin notes about key issues"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the keys were created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the keys were last updated"
    )
    
    class Meta:
        db_table = 'dm_user_keys'
        verbose_name = 'User API Keys'
        verbose_name_plural = 'User API Keys'
        ordering = ['-updated_at']
        
    def __str__(self) -> str:
        return f"API Keys for {self.dungeonmaster}"
    
    def save(self, *args, **kwargs):
        """
        Override save to set default usage statistics if not present.
        """
        if not self.usage_statistics:
            self.usage_statistics = {
                "openai": {"requests_today": 0, "last_request": None},
                "anthropic": {"requests_today": 0, "last_request": None},
                "google": {"requests_today": 0, "last_request": None},
                "deepseek": {"requests_today": 0, "last_request": None}
            }
        super().save(*args, **kwargs)
    
    def get_configured_providers(self):
        """Get list of configured API providers."""
        providers = []
        if self.openai_status == 'configured':
            providers.append('openai')
        if self.anthropic_status == 'configured':
            providers.append('anthropic')
        if self.google_status == 'configured':
            providers.append('google')
        if self.deepseek_status == 'configured':
            providers.append('deepseek')
        return providers
    
    def is_provider_configured(self, provider: str) -> bool:
        """Check if a specific provider is configured."""
        return getattr(self, f"{provider}_status", None) == 'configured'
    
    def mark_provider_invalid(self, provider: str):
        """Mark a provider's key as invalid."""
        if hasattr(self, f"{provider}_status"):
            setattr(self, f"{provider}_status", 'invalid')
            self.save()
    
    def mark_provider_configured(self, provider: str):
        """Mark a provider's key as configured."""
        if hasattr(self, f"{provider}_status"):
            setattr(self, f"{provider}_status", 'configured')
            setattr(self, f"{provider}_last_validated", timezone.now())
            self.save()
    
    def increment_usage(self, provider: str):
        """Increment usage counter for a provider."""
        if provider in self.usage_statistics:
            self.usage_statistics[provider]["requests_today"] += 1
            self.usage_statistics[provider]["last_request"] = timezone.now().isoformat()
            self.save()
    
    def reset_daily_usage(self):
        """Reset daily usage counters for all providers."""
        for provider in self.usage_statistics:
            self.usage_statistics[provider]["requests_today"] = 0
        self.save() 