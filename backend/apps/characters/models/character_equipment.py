import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .character import Character


class CharacterEquipment(models.Model):
    """
    Character equipment and items
    """
    EQUIPMENT_TYPE_CHOICES = [
        ('weapon', 'Waffe'),
        ('armor', 'Rüstung'),
        ('shield', 'Schild'),
        ('tool', 'Werkzeug'),
        ('consumable', 'Verbrauchsmaterial'),
        ('treasure', 'Schatz'),
        ('clothing', 'Kleidung'),
        ('container', 'Behälter'),
        ('other', 'Sonstiges')
    ]
    
    EQUIPMENT_STATUS_CHOICES = [
        ('equipped', 'Angelegt'),
        ('carried', 'Getragen'),
        ('stored', 'Gelagert'),
        ('broken', 'Beschädigt'),
        ('lost', 'Verloren')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='character_equipment')
    
    # Equipment data (JSON)
    equipment_data = models.JSONField()
    # Example: {"name": "Anderthalbhänder", "type": "weapon", "damage": "1W6+4", "weight": 2.5}
    
    # Equipment type
    equipment_type = models.CharField(
        max_length=20,
        choices=EQUIPMENT_TYPE_CHOICES,
        default='other'
    )
    
    # Equipment status
    status = models.CharField(
        max_length=20,
        choices=EQUIPMENT_STATUS_CHOICES,
        default='carried'
    )
    
    # Quantity
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Equipment condition (0-100)
    condition = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Equipment modifications (JSON)
    modifications = models.JSONField(default=dict)
    # Example: {"enchantment": "fire_damage", "custom_name": "Flammenschwert", "durability_bonus": 10}
    
    # Acquisition data (JSON)
    acquisition_data = models.JSONField(default=dict)
    # Example: {"acquisition_method": "purchase", "cost": 150, "acquisition_date": "2025-01-26"}
    
    # Location data (JSON)
    location_data = models.JSONField(default=dict)
    # Example: {"container": "Rucksack", "position": "main_compartment", "secured": true}
    
    # Usage history (JSON)
    usage_history = models.JSONField(default=list)
    # Example: [{"date": "2025-01-26", "action": "combat", "condition_change": -5}]
    
    # Notes and description
    notes = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chr_character_equipment'
        verbose_name = 'Character Equipment'
        verbose_name_plural = 'Character Equipment'
    
    def __str__(self):
        equipment_name = self.equipment_data.get('name', 'Unknown')
        return f"{self.character.name} - {equipment_name} ({self.get_status_display()})"
    
    def get_equipment_name(self):
        """Get the name of the equipment"""
        return self.equipment_data.get('name')
    
    def get_equipment_weight(self):
        """Get the weight of the equipment"""
        return self.equipment_data.get('weight', 0)
    
    def get_total_weight(self):
        """Get total weight including quantity"""
        return self.get_equipment_weight() * self.quantity
    
    def get_equipment_value(self):
        """Get the base value of the equipment"""
        return self.equipment_data.get('value', 0)
    
    def get_total_value(self):
        """Get total value including quantity and modifications"""
        base_value = self.get_equipment_value() * self.quantity
        
        # Add value from modifications
        modification_value = self.modifications.get('value_modifier', 0)
        
        return base_value + modification_value
    
    def get_modification(self, modification_type):
        """Get specific modification"""
        return self.modifications.get(modification_type)
    
    def has_modification(self, modification_type):
        """Check if equipment has specific modification"""
        return modification_type in self.modifications
    
    def add_modification(self, modification_type, value):
        """Add a modification to this equipment"""
        self.modifications[modification_type] = value
        self.save()
    
    def remove_modification(self, modification_type):
        """Remove a modification from this equipment"""
        if modification_type in self.modifications:
            del self.modifications[modification_type]
            self.save()
    
    def get_acquisition_method(self):
        """Get how the equipment was acquired"""
        return self.acquisition_data.get('acquisition_method')
    
    def get_acquisition_cost(self):
        """Get acquisition cost"""
        return self.acquisition_data.get('cost', 0)
    
    def get_acquisition_date(self):
        """Get when the equipment was acquired"""
        return self.acquisition_data.get('acquisition_date')
    
    def get_location(self):
        """Get current location"""
        return self.location_data.get('container')
    
    def get_position(self):
        """Get position within container"""
        return self.location_data.get('position')
    
    def is_secured(self):
        """Check if equipment is secured"""
        return self.location_data.get('secured', False)
    
    def set_status(self, new_status):
        """Set equipment status"""
        if new_status in dict(self.EQUIPMENT_STATUS_CHOICES):
            self.status = new_status
            self.save()
    
    def change_condition(self, change_amount):
        """Change equipment condition"""
        new_condition = max(0, min(100, self.condition + change_amount))
        self.condition = new_condition
        
        # Add to usage history
        from django.utils import timezone
        self.usage_history.append({
            'date': timezone.now().isoformat(),
            'action': 'condition_change',
            'condition_change': change_amount,
            'new_condition': new_condition
        })
        self.save()
    
    def add_usage_record(self, action, details=None):
        """Add usage record to history"""
        from django.utils import timezone
        usage_record = {
            'date': timezone.now().isoformat(),
            'action': action,
            'details': details or {}
        }
        self.usage_history.append(usage_record)
        self.save()
    
    def is_equipped(self):
        """Check if equipment is equipped"""
        return self.status == 'equipped'
    
    def is_carried(self):
        """Check if equipment is carried"""
        return self.status == 'carried'
    
    def is_stored(self):
        """Check if equipment is stored"""
        return self.status == 'stored'
    
    def is_broken(self):
        """Check if equipment is broken"""
        return self.condition <= 0
    
    def can_be_used(self):
        """Check if equipment can be used"""
        return self.condition > 0 and self.status != 'lost' 