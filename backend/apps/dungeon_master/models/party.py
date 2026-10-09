"""
Party system models for group management and role switching.
"""
import uuid
from django.db import models
from .user import ArcanoviUser


class Party(models.Model):
    """
    A party represents a group of users who play together.
    Multiple parties can exist, and users can be in multiple parties.
    """
    
    entity_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Unique entity identifier with format: PT-{12_digit_id}"
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Name of the party"
    )
    
    description = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Description of the party"
    )
    
    creator = models.ForeignKey(
        ArcanoviUser,
        on_delete=models.CASCADE,
        related_name='created_parties',
        help_text="User who created this party"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this party is active"
    )
    
    is_public = models.BooleanField(
        default=False,
        help_text="Can others discover this party?"
    )
    
    max_members = models.IntegerField(
        default=8,
        help_text="Maximum party size"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the party was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the party was last updated"
    )
    
    class Meta:
        db_table = 'dm_party'
        verbose_name = 'Party'
        verbose_name_plural = 'Parties'
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        """
        Override save to generate entity_id if not present.
        """
        if not self.entity_id:
            # Generate 12-digit unique ID
            unique_id = str(uuid.uuid4().int)[:12]
            self.entity_id = f"PT-{unique_id}"
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.name} ({self.entity_id})"
    
    @property
    def member_count(self) -> int:
        """Return the number of active members in this party."""
        return self.memberships.filter(status='active').count()
    
    @property
    def is_full(self) -> bool:
        """Check if party has reached maximum capacity."""
        return self.member_count >= self.max_members
    
    def get_dungeon_masters(self):
        """Get all users with dungeon_master role in this party."""
        return self.memberships.filter(
            role='dungeon_master',
            status='active'
        ).select_related('user')
    
    def get_players(self):
        """Get all users with player role in this party."""
        return self.memberships.filter(
            role='player',
            status='active'
        ).select_related('user')
    
    def get_active_members(self):
        """Get all active members regardless of role."""
        return self.memberships.filter(
            status='active'
        ).select_related('user')


class PartyMembership(models.Model):
    """
    Defines the relationship between users and parties.
    Tracks roles, permissions, and membership status.
    """
    
    ROLE_CHOICES = [
        ('player', 'Player'),
        ('dungeon_master', 'Dungeon Master'),
        ('co_dm', 'Co-Dungeon Master'),
        ('observer', 'Observer'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('invited', 'Invited'),
        ('banned', 'Banned'),
    ]
    
    user = models.ForeignKey(
        ArcanoviUser,
        on_delete=models.CASCADE,
        related_name='party_memberships',
        help_text="User who is a member of the party"
    )
    
    party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        related_name='memberships',
        help_text="Party that the user is a member of"
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='player',
        help_text="Role of the user in this party"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='invited',
        help_text="Status of the membership"
    )
    
    # Permissions
    can_invite_members = models.BooleanField(
        default=False,
        help_text="Can invite new members to the party"
    )
    
    can_manage_campaigns = models.BooleanField(
        default=False,
        help_text="Can create and manage campaigns"
    )
    
    can_edit_party = models.BooleanField(
        default=False,
        help_text="Can edit party details"
    )
    
    can_change_roles = models.BooleanField(
        default=False,
        help_text="Can change other members' roles"
    )
    
    can_remove_members = models.BooleanField(
        default=False,
        help_text="Can remove other members from the party"
    )
    
    joined_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the user joined the party"
    )
    
    last_active = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the user was last active in the party"
    )
    
    class Meta:
        db_table = 'dm_party_membership'
        verbose_name = 'Party Membership'
        verbose_name_plural = 'Party Memberships'
        unique_together = ['user', 'party']
        ordering = ['-joined_at']
        
    def __str__(self) -> str:
        return f"{self.user.full_name} - {self.party.name} ({self.role})"
    
    def save(self, *args, **kwargs):
        """
        Override save to set default permissions based on role.
        """
        if self.role == 'dungeon_master':
            # DMs get most permissions by default
            self.can_invite_members = True
            self.can_manage_campaigns = True
            self.can_edit_party = True
            self.can_change_roles = True
            self.can_remove_members = True
        elif self.role == 'co_dm':
            # Co-DMs get campaign management permissions
            self.can_manage_campaigns = True
            self.can_invite_members = True
        elif self.role == 'player':
            # Players get basic permissions
            self.can_invite_members = False
            self.can_manage_campaigns = False
            self.can_edit_party = False
            self.can_change_roles = False
            self.can_remove_members = False
        elif self.role == 'observer':
            # Observers get no permissions
            self.can_invite_members = False
            self.can_manage_campaigns = False
            self.can_edit_party = False
            self.can_change_roles = False
            self.can_remove_members = False
        
        super().save(*args, **kwargs)
    
    def promote_to_dm(self):
        """Promote this member to dungeon master role."""
        self.role = 'dungeon_master'
        self.save()
    
    def demote_to_player(self):
        """Demote this member to player role."""
        self.role = 'player'
        self.save()
    
    def make_co_dm(self):
        """Make this member a co-dungeon master."""
        self.role = 'co_dm'
        self.save()
    
    def activate(self):
        """Activate this membership (accept invitation)."""
        self.status = 'active'
        self.save()
    
    def deactivate(self):
        """Deactivate this membership."""
        self.status = 'inactive'
        self.save()
    
    def ban(self):
        """Ban this member from the party."""
        self.status = 'banned'
        self.save()


class Campaign(models.Model):
    """
    A campaign is a series of game sessions run by a party.
    Each campaign has a primary DM but can have multiple co-DMs.
    """
    
    entity_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Unique entity identifier with format: CM-{12_digit_id}"
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Name of the campaign"
    )
    
    description = models.TextField(
        max_length=2000,
        blank=True,
        help_text="Description of the campaign"
    )
    
    party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        related_name='campaigns',
        help_text="Party that runs this campaign"
    )
    
    primary_dm = models.ForeignKey(
        ArcanoviUser,
        on_delete=models.CASCADE,
        related_name='primary_campaigns',
        help_text="Primary dungeon master for this campaign"
    )
    
    co_dms = models.ManyToManyField(
        ArcanoviUser,
        blank=True,
        related_name='co_campaigns',
        help_text="Co-dungeon masters for this campaign"
    )
    
    # Campaign Settings
    game_system = models.CharField(
        max_length=100,
        default='D&D 5e',
        help_text="Game system used for this campaign"
    )
    
    content_rating = models.CharField(
        max_length=20,
        default='teen',
        help_text="Content rating for this campaign"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this campaign is active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the campaign was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the campaign was last updated"
    )
    
    class Meta:
        db_table = 'dm_campaign'
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        """
        Override save to generate entity_id if not present.
        """
        if not self.entity_id:
            # Generate 12-digit unique ID
            unique_id = str(uuid.uuid4().int)[:12]
            self.entity_id = f"CM-{unique_id}"
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.name} ({self.entity_id})"
    
    def transfer_dm_role(self, new_dm: ArcanoviUser):
        """Transfer primary DM role to another user."""
        if new_dm in [membership.user for membership in self.party.get_active_members()]:
            old_dm = self.primary_dm
            self.primary_dm = new_dm
            self.save()
            
            # Update party memberships
            try:
                old_membership = PartyMembership.objects.get(user=old_dm, party=self.party)
                old_membership.demote_to_player()
            except PartyMembership.DoesNotExist:
                pass
            
            try:
                new_membership = PartyMembership.objects.get(user=new_dm, party=self.party)
                new_membership.promote_to_dm()
            except PartyMembership.DoesNotExist:
                pass
    
    def add_co_dm(self, user: ArcanoviUser):
        """Add a co-dungeon master to this campaign."""
        if user in [membership.user for membership in self.party.get_active_members()]:
            self.co_dms.add(user)
            
            # Update party membership
            try:
                membership = PartyMembership.objects.get(user=user, party=self.party)
                membership.make_co_dm()
            except PartyMembership.DoesNotExist:
                pass
    
    def remove_co_dm(self, user: ArcanoviUser):
        """Remove a co-dungeon master from this campaign."""
        self.co_dms.remove(user)
        
        # Update party membership back to player
        try:
            membership = PartyMembership.objects.get(user=user, party=self.party)
            membership.demote_to_player()
        except PartyMembership.DoesNotExist:
            pass
    
    @property
    def all_dms(self):
        """Get all DMs (primary + co-DMs) for this campaign."""
        co_dm_list = list(self.co_dms.all())
        return [self.primary_dm] + co_dm_list 