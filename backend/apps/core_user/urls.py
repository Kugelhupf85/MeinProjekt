"""
URL configuration for core_user app.
"""
from django.urls import path, include

app_name = 'core_user'

urlpatterns = [
    # Authentication endpoints
    path('', include('apps.core_user.api.urls.auth.auth_urls')),
    
    # Profile management endpoints  
    path('', include('apps.core_user.api.urls.profile.profile_urls')),
    
    # Security management endpoints
    path('', include('apps.core_user.api.urls.security.security_urls')),
] 