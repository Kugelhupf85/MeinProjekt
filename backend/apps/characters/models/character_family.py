import uuid
from django.db import models
from .character import Character


class CharacterFamily(models.Model):
    """
    Character family relationships and genealogy
    """
    RELATIONSHIP_TYPE_CHOICES = [
        ('parent', 'Elternteil'),
        ('child', 'Kind'),
        ('sibling', 'Geschwister'),
        ('spouse', 'Ehepartner'),
        ('grandparent', 'Großelternteil'),
        ('grandchild', 'Enkelkind'),
        ('cousin', 'Cousin/Cousine'),
        ('uncle_aunt', 'Onkel/Tante'),
        ('niece_nephew', 'Nichte/Neffe'),
        ('ancestor', 'Vorfahr'),
        ('descendant', 'Nachkomme'),
        ('other', 'Sonstiger Verwandter')
    ]
    
    RELATIONSHIP_STATUS_CHOICES = [
        ('alive', 'Lebend'),
        ('deceased', 'Verstorben'),
        ('missing', 'Vermisst'),
        ('unknown', 'Unbekannt')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='family_relationships')
    
    # Related character (if in same system)
    related_character = models.ForeignKey(
        Character, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='related_family_members'
    )
    
    # Relationship type
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_TYPE_CHOICES,
        default='other'
    )
    
    # Relationship status
    relationship_status = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_STATUS_CHOICES,
        default='alive'
    )
    
    # Family member data (JSON) - for external family members
    family_member_data = models.JSONField(default=dict)
    # Example: {"name": "Vater", "age": 45, "profession": "Bauer", "location": "Dorf"}
    
    # Relationship details (JSON)
    relationship_details = models.JSONField(default=dict)
    # Example: {"strength": "strong", "quality": "loving", "contact_frequency": "weekly"}
    
    # Family history (JSON)
    family_history = models.JSONField(default=list)
    # Example: [{"date": "2025-01-26", "event": "birth", "details": "Geboren in Gareth"}]
    
    # Inheritance and legacy (JSON)
    inheritance_data = models.JSONField(default=dict)
    # Example: {"inheritance_type": "property", "value": 1000, "conditions": ["age_requirement"]}
    
    # Notes and description
    notes = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chr_character_family'
        verbose_name = 'Character Family'
        verbose_name_plural = 'Character Family'
        unique_together = ['character', 'related_character', 'relationship_type']
    
    def __str__(self):
        if self.related_character:
            return f"{self.character.name} - {self.get_relationship_type_display()} - {self.related_character.name}"
        else:
            family_name = self.family_member_data.get('name', 'Unknown')
            return f"{self.character.name} - {self.get_relationship_type_display()} - {family_name}"
    
    def get_family_member_name(self):
        """Get the name of the family member"""
        if self.related_character:
            return self.related_character.name
        return self.family_member_data.get('name', 'Unknown')
    
    def get_family_member_age(self):
        """Get the age of the family member"""
        if self.related_character:
            # Character model doesn't have age attribute, so return None for internal characters
            return None
        return self.family_member_data.get('age')
    
    def get_family_member_profession(self):
        """Get the profession of the family member"""
        if self.related_character:
            return self.related_character.profession
        return self.family_member_data.get('profession')
    
    def get_family_member_location(self):
        """Get the location of the family member"""
        if self.related_character:
            return self.related_character.location
        return self.family_member_data.get('location')
    
    def get_relationship_strength(self):
        """Get the strength of the relationship"""
        return self.relationship_details.get('strength', 'normal')
    
    def get_relationship_quality(self):
        """Get the quality of the relationship"""
        return self.relationship_details.get('quality', 'neutral')
    
    def get_contact_frequency(self):
        """Get how often contact is maintained"""
        return self.relationship_details.get('contact_frequency', 'rarely')
    
    def add_family_event(self, event_type, details=None):
        """Add a family event to history"""
        from django.utils import timezone
        family_event = {
            'date': timezone.now().isoformat(),
            'event': event_type,
            'details': details or {}
        }
        self.family_history.append(family_event)
        self.save()
    
    def add_family_history_event(self, event_type, details=None):
        """Add a family history event (alias for add_family_event)"""
        return self.add_family_event(event_type, details)
    
    def get_inheritance_share(self):
        """Get inheritance share as decimal (0.0 to 1.0)"""
        return self.inheritance_data.get('share', 0.0)
    
    def get_inheritance_type(self):
        """Get inheritance type"""
        return self.inheritance_data.get('inheritance_type')
    
    def get_inheritance_value(self):
        """Get inheritance value"""
        return self.inheritance_data.get('value', 0)
    
    def get_inheritance_conditions(self):
        """Get inheritance conditions"""
        return self.inheritance_data.get('conditions', [])
    
    def is_alive(self):
        """Check if family member is alive"""
        return self.relationship_status == 'alive'
    
    def is_deceased(self):
        """Check if family member is deceased"""
        return self.relationship_status == 'deceased'
    
    def is_missing(self):
        """Check if family member is missing"""
        return self.relationship_status == 'missing'
    
    def is_internal_character(self):
        """Check if family member is a character in the system"""
        return self.related_character is not None
    
    def is_external_person(self):
        """Check if family member is an external person"""
        return self.related_character is None 