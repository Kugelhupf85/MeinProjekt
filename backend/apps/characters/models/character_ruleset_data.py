import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class CharacterRuleSetData(models.Model):
    """
    Extended RuleSet-specific data for characters (primarily DSA 4.1)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    character = models.OneToOneField('Character', on_delete=models.CASCADE, related_name='ruleset_data')
    
    # DSA 4.1 Specific Fields
    # Generation Data (wichtig für Charaktererstellung)
    generation_points_max = models.IntegerField(default=110, validators=[MinValueValidator(0), MaxValueValidator(200)])
    generation_points_attributes_max = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(200)])
    attribute_maximum = models.IntegerField(default=14, validators=[MinValueValidator(8), MaxValueValidator(20)])
    
    # Experience & Level
    xp_total = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    xp_current = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(50)])
    
    # Personal Data
    birthday = models.CharField(max_length=50, blank=True)
    age = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(200)])
    weight = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(500)])  # in kg
    height = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(300)])  # in cm
    gender = models.CharField(max_length=20, blank=True)
    hair_color = models.CharField(max_length=30, blank=True)
    eye_color = models.CharField(max_length=30, blank=True)
    
    # DSA 4.1 Derived Values (calculated from core_attributes)
    magic_resistance = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(50)])  # Magieresistenz (MR)
    life_energy = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(200)])       # Lebensenergie (LE)
    endurance = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(200)])         # Ausdauer (AU)
    astral_energy = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(200)])  # Astralenergie (AE) - nur für Magier
    karma_energy = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(200)])   # Karmaenergie (KE) - nur für Geweihte
    
    # Combat Values
    attack_base = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(50)])       # Attacke-Basis (AT)
    parade_base = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(50)])       # Parade-Basis (PA)
    ranged_combat_base = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(50)]) # Fernkampf-Basis (FK)
    initiative = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(50)])        # Initiative (INI)
    
    # Social Values
    social_status = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(20)])     # Sozialstatus
    guild_membership = models.CharField(max_length=100, blank=True)  # Gildenzugehörigkeit
    
    # Extended Data (JSON for flexibility)
    extended_data = models.JSONField(default=dict)
    # For future RuleSets or additional data
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'characters_character_ruleset_data'
        verbose_name = 'Character Rule Set Data'
        verbose_name_plural = 'Character Rule Set Data'
    
    def __str__(self):
        return f"Data for {self.character.name}"
    
    def calculate_derived_values(self):
        """Calculate DSA 4.1 derived values from core attributes"""
        if not self.character.core_attributes:
            return
        
        attrs = self.character.core_attributes
        
        # Basic DSA 4.1 calculations
        self.life_energy = (attrs.get('KO', 0) * 2) + attrs.get('KK', 0) + 6
        self.endurance = (attrs.get('KO', 0) * 2) + attrs.get('GE', 0) + 6
        self.magic_resistance = (attrs.get('MU', 0) + attrs.get('KL', 0) + attrs.get('KO', 0)) // 5
        self.initiative = (attrs.get('MU', 0) + attrs.get('GE', 0)) // 2
        self.attack_base = (attrs.get('MU', 0) + attrs.get('GE', 0) + attrs.get('KK', 0)) // 5
        self.parade_base = (attrs.get('IN', 0) + attrs.get('GE', 0) + attrs.get('KK', 0)) // 5
        self.ranged_combat_base = (attrs.get('IN', 0) + attrs.get('FF', 0) + attrs.get('KK', 0)) // 5
    
    def save(self, *args, **kwargs):
        """Override save to calculate derived values"""
        self.calculate_derived_values()
        super().save(*args, **kwargs)
    
    @property
    def generation_points_used(self):
        """Calculate used generation points"""
        if not self.character.core_attributes:
            return 0
        
        # Base cost: 8 points per attribute (8 attributes * 8 = 64)
        base_cost = 64
        total_attr_points = sum(self.character.core_attributes.values())
        return total_attr_points - base_cost
    
    @property
    def generation_points_remaining(self):
        """Calculate remaining generation points"""
        return self.generation_points_max - self.generation_points_used
    
    @property
    def is_generation_valid(self):
        """Check if character generation is valid"""
        return self.generation_points_remaining >= 0
    
    def get_extended_data(self, key, default=None):
        """Get extended data value"""
        return self.extended_data.get(key, default)
    
    def set_extended_data(self, key, value):
        """Set extended data value"""
        self.extended_data[key] = value
        self.save() 