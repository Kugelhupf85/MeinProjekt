"""
URL configuration for UserKeys API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import UserKeysViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'user-keys', UserKeysViewSet, basename='userkeys')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]

# Available endpoints:
# GET    /api/user-keys/                               - List UserKeys
# POST   /api/user-keys/                               - Create UserKeys
# GET    /api/user-keys/{id}/                          - Retrieve specific UserKeys
# PUT    /api/user-keys/{id}/                          - Update UserKeys (full)
# PATCH  /api/user-keys/{id}/                          - Update UserKeys (partial)
# DELETE /api/user-keys/{id}/                          - Delete UserKeys
# GET    /api/user-keys/my-keys/                       - Get current user's keys
# POST   /api/user-keys/{id}/set-key/                  - Set/update API key
# POST   /api/user-keys/{id}/delete-key/               - Delete API key
# GET    /api/user-keys/{id}/check-status/?provider=   - Check key status
# GET    /api/user-keys/{id}/usage-stats/?provider=    - Get usage statistics
# POST   /api/user-keys/{id}/increment-usage/          - Increment usage counter
# POST   /api/user-keys/{id}/reset-usage/              - Reset usage statistics
# POST   /api/user-keys/{id}/validate-key/             - Validate API key
# GET    /api/user-keys/{id}/configured-providers/     - Get configured providers 