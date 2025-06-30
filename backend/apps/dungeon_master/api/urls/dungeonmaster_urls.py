"""
URL configuration for DungeonMaster API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import DungeonMasterViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'dungeon-masters', DungeonMasterViewSet, basename='dungeonmaster')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]

# Available endpoints:
# GET    /api/dungeon-masters/                     - List all DungeonMasters
# POST   /api/dungeon-masters/                     - Create new DungeonMaster
# GET    /api/dungeon-masters/{id}/                - Retrieve specific DungeonMaster
# PUT    /api/dungeon-masters/{id}/                - Update DungeonMaster (full)
# PATCH  /api/dungeon-masters/{id}/                - Update DungeonMaster (partial)
# DELETE /api/dungeon-masters/{id}/                - Delete DungeonMaster
# GET    /api/dungeon-masters/profile/             - Get current user's profile
# GET    /api/dungeon-masters/public/              - Get public profiles
# PATCH  /api/dungeon-masters/{id}/update-user/    - Update User info
# POST   /api/dungeon-masters/{id}/toggle-public/ - Toggle public visibility
# POST   /api/dungeon-masters/{id}/add-green-flag/ - Add green flag
# POST   /api/dungeon-masters/{id}/remove-green-flag/ - Remove green flag
# POST   /api/dungeon-masters/{id}/add-red-flag/   - Add red flag
# POST   /api/dungeon-masters/{id}/remove-red-flag/ - Remove red flag
# POST   /api/dungeon-masters/{id}/add-theme-preference/ - Add theme preference
# POST   /api/dungeon-masters/{id}/remove-theme-preference/ - Remove theme preference 