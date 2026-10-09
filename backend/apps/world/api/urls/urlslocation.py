"""
Location URL Configuration
"""

from django.urls import path
from apps.world.api.views import viewlocation

urlpatterns = [
    # Location CRUD operations
    path('worlds/<int:world_id>/locations/', viewlocation.location_list, name='location_list'),
    path('worlds/<int:world_id>/regions/<int:region_id>/locations/', viewlocation.location_list, name='location_list_by_region'),
    path('worlds/<int:world_id>/regions/<int:region_id>/locations/create/', viewlocation.location_create, name='location_create'),
    path('worlds/<int:world_id>/regions/<int:region_id>/locations/<int:location_id>/', viewlocation.location_detail, name='location_detail'),
    
    # Location statistics and search
    path('worlds/<int:world_id>/regions/<int:region_id>/locations/<int:location_id>/statistics/', viewlocation.location_statistics, name='location_statistics'),
    path('worlds/<int:world_id>/locations/search/', viewlocation.location_search, name='location_search'),
    path('worlds/<int:world_id>/locations/type/<str:location_type>/', viewlocation.location_by_type, name='location_by_type'),
] 