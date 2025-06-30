"""
Main URL configuration for the adventure app.
"""
from django.urls import path, include

app_name = 'adventure'

urlpatterns = [
    # Adventure campaign management endpoints
    path('', include('apps.adventure.api.urls.urlscampaign')),
] 