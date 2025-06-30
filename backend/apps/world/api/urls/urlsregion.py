"""
Region URL Configuration
"""

from django.urls import path
from apps.world.api.endpoints.viewregion import (
    create_region, get_region, list_regions, update_region, 
    delete_region, search_regions, get_region_statistics
)

urlpatterns = [
    # Region CRUD operations
    path('', list_regions, name='list_regions'),
    path('create/', create_region, name='create_region'),
    path('<str:region_id>/', get_region, name='get_region'),
    path('<str:region_id>/update/', update_region, name='update_region'),
    path('<str:region_id>/delete/', delete_region, name='delete_region'),
    
    # Region search and statistics
    path('search/', search_regions, name='search_regions'),
    path('<str:region_id>/statistics/', get_region_statistics, name='get_region_statistics'),
] 