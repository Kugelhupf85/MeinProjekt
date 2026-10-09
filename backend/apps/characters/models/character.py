import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Character(models.Model):
    """
    Core Character Model with User, World and RuleSet relationships
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey('core_user.User', on_delete=models.CASCADE, related_name='characters')
    world = models.ForeignKey('world.World', on_delete=models.CASCADE, related_name='characters')
    rule_set = models.ForeignKey('RuleSet', on_delete=models.PROTECT, related_name='characters')
    
    # Basic Character Info
    name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # Core Attributes (JSON - flexible per RuleSet)
    core_attributes = models.JSONField(default=dict)
    # Example: {"rule_set": "dsa_4_1", "MU": 14, "KL": 13, "IN": 12, ...}
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'characters_character'
        unique_together = ['user', 'world', 'name']
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'
    
    def __str__(self):
        return f"{self.name} ({self.rule_set.display_name})"
    
    def clean(self):
        """Validate character data"""
        super().clean()
        
        # Validate core attributes against rule set schema
        if self.rule_set and self.core_attributes:
            schema = self.rule_set.get_attribute_schema()
            if schema:
                self._validate_attributes_against_schema(schema)
    
    def _validate_attributes_against_schema(self, schema):
        """Validate core attributes against the rule set schema"""
        required_attrs = schema.get('required', [])
        properties = schema.get('properties', {})
        
        # Check required attributes
        for attr in required_attrs:
            if attr not in self.core_attributes:
                raise ValidationError(f"Required attribute '{attr}' is missing")
        
        # Check attribute constraints
        for attr, value in self.core_attributes.items():
            if attr in properties:
                attr_schema = properties[attr]
                
                # Check type
                if attr_schema.get('type') == 'integer' and not isinstance(value, int):
                    raise ValidationError(f"Attribute '{attr}' must be an integer")
                
                # Check minimum/maximum
                if 'minimum' in attr_schema and value < attr_schema['minimum']:
                    raise ValidationError(f"Attribute '{attr}' ({value}) is below minimum ({attr_schema['minimum']})")
                
                if 'maximum' in attr_schema and value > attr_schema['maximum']:
                    raise ValidationError(f"Attribute '{attr}' ({value}) exceeds maximum ({attr_schema['maximum']})")
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_draft(self):
        """Check if character is in draft status"""
        return self.status == 'draft'
    
    @property
    def is_active(self):
        """Check if character is active"""
        return self.status == 'active'
    
    @property
    def is_archived(self):
        """Check if character is archived"""
        return self.status == 'archived'
    
    def activate(self):
        """Activate the character"""
        self.status = 'active'
        self.save()
    
    def archive(self):
        """Archive the character"""
        self.status = 'archived'
        self.save()
    
    def get_core_attribute(self, attribute_name):
        """Get a specific core attribute value"""
        return self.core_attributes.get(attribute_name)
    
    def set_core_attribute(self, attribute_name, value):
        """Set a specific core attribute value"""
        self.core_attributes[attribute_name] = value
        self.save() 