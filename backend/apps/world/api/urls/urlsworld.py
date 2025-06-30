"""
World URL Configuration
"""

from django.urls import path
from apps.world.api.endpoints.viewworld import (
    create_world, get_world, list_worlds, update_world, 
    delete_world, search_worlds, get_world_statistics
)

urlpatterns = [
    # World CRUD operations
    path('', list_worlds, name='list_worlds'),
    path('create/', create_world, name='create_world'),
    path('<str:world_id>/', get_world, name='get_world'),
    path('<str:world_id>/update/', update_world, name='update_world'),
    path('<str:world_id>/delete/', delete_world, name='delete_world'),
    
    # World search and statistics
    path('search/', search_worlds, name='search_worlds'),
    path('<str:world_id>/statistics/', get_world_statistics, name='get_world_statistics'),
] 