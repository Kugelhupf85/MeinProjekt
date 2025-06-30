"""
URL configuration for UserSettings API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import UserSettingsViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'user-settings', UserSettingsViewSet, basename='usersettings')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]

# Available endpoints:
# GET    /api/user-settings/                           - List UserSettings
# POST   /api/user-settings/                           - Create UserSettings
# GET    /api/user-settings/{id}/                      - Retrieve specific UserSettings
# PUT    /api/user-settings/{id}/                      - Update UserSettings (full)
# PATCH  /api/user-settings/{id}/                      - Update UserSettings (partial)
# DELETE /api/user-settings/{id}/                      - Delete UserSettings
# GET    /api/user-settings/my-settings/               - Get current user's settings
# PATCH  /api/user-settings/{id}/ui-setting/           - Update specific UI setting
# PATCH  /api/user-settings/{id}/ai-setting/           - Update specific AI setting
# PATCH  /api/user-settings/{id}/feature-flag/         - Update specific feature flag
# PATCH  /api/user-settings/{id}/privacy-setting/      - Update specific privacy setting
# GET    /api/user-settings/{id}/get-ui-setting/?key=  - Get specific UI setting
# GET    /api/user-settings/{id}/get-ai-setting/?key=  - Get specific AI setting
# GET    /api/user-settings/{id}/get-feature-flag/?key= - Get specific feature flag
# GET    /api/user-settings/{id}/get-privacy-setting/?key= - Get specific privacy setting
# POST   /api/user-settings/{id}/reset-to-defaults/    - Reset all settings to defaults 