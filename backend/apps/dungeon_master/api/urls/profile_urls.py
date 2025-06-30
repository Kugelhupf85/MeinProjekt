"""
URL configuration for DungeonMaster profile management endpoints.
"""
from django.urls import path
from ..views.profile_views import (
    profile_settings,
    profile_summary,
    quick_setting_update,
    initialize_profile,
)

urlpatterns = [
    # Profile settings management (secure form endpoint)
    path('profile/settings/', profile_settings, name='profile_settings'),
    
    # Profile summary for dashboard
    path('profile/summary/', profile_summary, name='profile_summary'),
    
    # Quick setting updates
    path('profile/quick-setting/', quick_setting_update, name='quick_setting_update'),
    
    # Initialize profile structure
    path('profile/initialize/', initialize_profile, name='initialize_profile'),
]

# Available endpoints:
# GET/POST /api/profile/settings/      - Secure profile settings form
# GET      /api/profile/summary/       - Profile summary for dashboard
# POST     /api/profile/quick-setting/ - Quick individual setting updates
# POST     /api/profile/initialize/    - Initialize profile structure 