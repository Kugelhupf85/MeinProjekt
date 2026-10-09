"""
World API URLs
"""

from django.urls import path
from apps.world.api.views import viewworld

urlpatterns = [
    # World CRUD
    path('', viewworld.world_list, name='world-list'),
    path('create/', viewworld.world_create, name='world-create'),
    path('<int:world_id>/', viewworld.world_detail, name='world-detail'),
    
    # World API Keys
    path('<int:world_id>/api-keys/', viewworld.world_api_keys_detail, name='world-api-keys-detail'),
    path('<int:world_id>/api-keys/update/', viewworld.world_api_keys_update, name='world-api-keys-update'),
    path('<int:world_id>/api-keys/test/', viewworld.world_api_keys_test, name='world-api-keys-test'),
    
    # World Party
    path('<int:world_id>/party/', viewworld.world_party_detail, name='world-party-detail'),
    path('<int:world_id>/party/update/', viewworld.world_party_update, name='world-party-update'),
    path('<int:world_id>/party/members/', viewworld.world_party_members, name='world-party-members'),
    path('<int:world_id>/party/invite/', viewworld.world_party_invite, name='world-party-invite'),
    path('<int:world_id>/party/members/<int:membership_id>/', viewworld.world_party_membership_update, name='world-party-membership-update'),
    path('<int:world_id>/party/members/<int:membership_id>/remove/', viewworld.world_party_membership_remove, name='world-party-membership-remove'),
] 