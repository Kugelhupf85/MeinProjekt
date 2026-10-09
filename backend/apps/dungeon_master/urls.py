"""
Main URL configuration for the dungeon_master app.
"""
from django.urls import path, include

app_name = 'dungeon_master'

urlpatterns = [
    # API endpoints for all dungeon master functionality
    path('api/', include('apps.dungeon_master.api.urls')),
]