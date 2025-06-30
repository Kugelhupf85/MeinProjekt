"""
URLs package for the dungeon_master app API.
"""
from django.urls import path, include

urlpatterns = [
    # Profile management endpoints (secure forms)
    path('', include('backend.apps.dungeon_master.api.urls.profile_urls')),
    
    # DungeonMaster endpoints
    path('', include('backend.apps.dungeon_master.api.urls.dungeonmaster_urls')),
    
    # UserSettings endpoints  
    path('', include('backend.apps.dungeon_master.api.urls.settings_urls')),
    
    # UserKeys endpoints
    path('', include('backend.apps.dungeon_master.api.urls.apikeys_urls')),
] 