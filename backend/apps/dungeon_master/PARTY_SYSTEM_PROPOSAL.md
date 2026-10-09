# Party System Design Proposal - Arcanovi

## Overview
This document outlines the design for a flexible party system that allows users to form groups, switch roles between Player and Dungeon Master, and manage campaigns together.

## Core Models

### 1. ArcanoviUser (Base User Model)
```python
class ArcanoviUser(AbstractUser):
    """
    Base user model for all Arcanovi users (Players and Dungeon Masters).
    Extends Django's AbstractUser to provide authentication and basic user data.
    """
    entity_id = models.CharField(max_length=20, unique=True)  # AU-{12_digit_id}
    display_name = models.CharField(max_length=200, blank=True)
    bio = models.TextField(max_length=2000, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 2. Party (Group Management)
```python
class Party(models.Model):
    """
    A party represents a group of users who play together.
    Multiple parties can exist, and users can be in multiple parties.
    """
    entity_id = models.CharField(max_length=20, unique=True)  # PT-{12_digit_id}
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True)
    creator = models.ForeignKey(ArcanoviUser, on_delete=models.CASCADE, related_name='created_parties')
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)  # Can others discover this party?
    max_members = models.IntegerField(default=8)  # Maximum party size
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 3. PartyMembership (User-Party Relationship)
```python
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
    
    user = models.ForeignKey(ArcanoviUser, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='player')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='invited')
    
    # Permissions
    can_invite_members = models.BooleanField(default=False)
    can_manage_campaigns = models.BooleanField(default=False)
    can_edit_party = models.BooleanField(default=False)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'party']
```

### 4. Campaign (Game Sessions)
```python
class Campaign(models.Model):
    """
    A campaign is a series of game sessions run by a party.
    Each campaign has a primary DM but can have multiple co-DMs.
    """
    entity_id = models.CharField(max_length=20, unique=True)  # CM-{12_digit_id}
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=2000, blank=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='campaigns')
    primary_dm = models.ForeignKey(ArcanoviUser, on_delete=models.CASCADE, related_name='primary_campaigns')
    co_dms = models.ManyToManyField(ArcanoviUser, blank=True, related_name='co_campaigns')
    
    # Campaign Settings
    game_system = models.CharField(max_length=100, default='D&D 5e')
    content_rating = models.CharField(max_length=20, default='teen')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 5. PlayerProfile & DungeonMasterProfile (Role-Specific Data)
```python
class PlayerProfile(models.Model):
    """
    Player-specific profile data and preferences.
    """
    user = models.OneToOneField(ArcanoviUser, on_delete=models.CASCADE, related_name='player_profile')
    
    # Player Preferences
    preferred_game_systems = models.JSONField(default=list)
    character_creation_preferences = models.JSONField(default=dict)
    playstyle_preferences = models.JSONField(default=dict)
    
    # Statistics
    campaigns_played = models.IntegerField(default=0)
    total_sessions = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DungeonMasterProfile(models.Model):
    """
    Dungeon Master-specific profile data and preferences.
    Separated from base user to keep DM-specific functionality clean.
    """
    user = models.OneToOneField(ArcanoviUser, on_delete=models.CASCADE, related_name='dm_profile')
    
    # DM Experience and Preferences (from current DungeonMaster model)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='beginner')
    strictness_level = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    green_flags = models.JSONField(default=list)
    red_flags = models.JSONField(default=list)
    content_rating = models.CharField(max_length=10, choices=CONTENT_RATING_CHOICES, default='teen')
    themes_preferences = models.JSONField(default=list)
    
    # Statistics
    campaigns_run = models.IntegerField(default=0)
    total_sessions_run = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Role Management System

### Role Switching Mechanism
1. **Flexible Roles**: Users can have different roles in different parties
2. **Role Promotion**: Party members can promote/demote other members (with permissions)
3. **DM Handoff**: Current DM can transfer primary DM role to another party member
4. **Co-DM System**: Multiple DMs can collaborate on a single campaign

### Permission System
```python
class PartyPermission(models.Model):
    """
    Granular permissions for party members.
    """
    membership = models.OneToOneField(PartyMembership, on_delete=models.CASCADE)
    
    # Campaign Management
    can_create_campaigns = models.BooleanField(default=False)
    can_edit_campaigns = models.BooleanField(default=False)
    can_delete_campaigns = models.BooleanField(default=False)
    
    # Member Management
    can_invite_members = models.BooleanField(default=False)
    can_remove_members = models.BooleanField(default=False)
    can_change_roles = models.BooleanField(default=False)
    
    # Party Management
    can_edit_party = models.BooleanField(default=False)
    can_delete_party = models.BooleanField(default=False)
```

## Implementation Strategy

### Phase 1: User System Migration
1. Create new `ArcanoviUser` model extending `AbstractUser`
2. Migrate existing `DungeonMaster` users to new system
3. Create `PlayerProfile` and `DungeonMasterProfile` models
4. Update authentication system

### Phase 2: Party System Implementation
1. Create `Party` and `PartyMembership` models
2. Implement invitation system
3. Create role management APIs
4. Build party management UI

### Phase 3: Campaign Integration
1. Create `Campaign` model linked to parties
2. Implement DM handoff functionality
3. Create co-DM collaboration features
4. Update existing campaign system

### Phase 4: Permission System
1. Implement granular permissions
2. Create role-based access control
3. Add admin/moderator capabilities
4. Security and validation

## Benefits of This Design

1. **Flexibility**: Users can be players in one party, DM in another
2. **Scalability**: Clean separation of concerns between user types
3. **Collaboration**: Multiple DMs can work together
4. **Growth**: Easy to add new roles and permissions
5. **Migration**: Existing DM data can be preserved and migrated

## API Endpoints Design

```
# User Management
POST /api/auth/register/          # Register new user
POST /api/auth/login/             # User login
GET  /api/users/profile/          # Get current user profile
PUT  /api/users/profile/          # Update user profile

# Party Management
GET    /api/parties/              # List user's parties
POST   /api/parties/              # Create new party
GET    /api/parties/{id}/         # Get party details
PUT    /api/parties/{id}/         # Update party
DELETE /api/parties/{id}/         # Delete party

# Membership Management
POST   /api/parties/{id}/invite/  # Invite user to party
POST   /api/parties/{id}/join/    # Join party (accept invitation)
PUT    /api/parties/{id}/members/{user_id}/role/  # Change member role
DELETE /api/parties/{id}/members/{user_id}/       # Remove member

# Campaign Management
GET    /api/parties/{id}/campaigns/     # List party campaigns
POST   /api/parties/{id}/campaigns/     # Create campaign
PUT    /api/campaigns/{id}/dm/          # Transfer DM role
POST   /api/campaigns/{id}/co-dm/       # Add co-DM
```

This design provides a solid foundation for a flexible, scalable party system that can grow with the application's needs. 