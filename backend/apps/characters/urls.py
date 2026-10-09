"""
Characters App URLs
Main URL configuration for the characters app
"""

from django.urls import path, include

app_name = 'characters'

urlpatterns = [
    path('', include('apps.characters.api.urls.character_urls')),
] 