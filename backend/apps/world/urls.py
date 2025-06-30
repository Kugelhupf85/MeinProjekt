"""
World App URL Configuration
"""

from django.urls import path, include

app_name = 'world'

urlpatterns = [
    # World management endpoints
    path('worlds/', include('apps.world.api.urls.urlsworld')),
    path('regions/', include('apps.world.api.urls.urlsregion')),
    path('locations/', include('apps.world.api.urls.urlslocation')),
] 