"""
Location URL Configuration
"""

from django.urls import path
from apps.world.api.endpoints.viewlocation import (
    create_location, get_location, list_locations, update_location, 
    delete_location, search_locations, get_location_statistics, get_locations_by_type
)

urlpatterns = [
    # Location CRUD operations
    path('', list_locations, name='list_locations'),
    path('create/', create_location, name='create_location'),
    path('<str:location_id>/', get_location, name='get_location'),
    path('<str:location_id>/update/', update_location, name='update_location'),
    path('<str:location_id>/delete/', delete_location, name='delete_location'),
    
    # Location search and statistics
    path('search/', search_locations, name='search_locations'),
    path('<str:location_id>/statistics/', get_location_statistics, name='get_location_statistics'),
    
    # Location filtering by type
    path('type/<str:location_type>/', get_locations_by_type, name='get_locations_by_type'),
] 