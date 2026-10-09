"""
Region URL Configuration
"""

from django.urls import path
from apps.world.api.views import viewregion

urlpatterns = [
    # Region CRUD operations
    path('worlds/<int:world_id>/regions/', viewregion.region_list, name='region_list'),
    path('worlds/<int:world_id>/regions/create/', viewregion.region_create, name='region_create'),
    path('worlds/<int:world_id>/regions/<int:region_id>/', viewregion.region_detail, name='region_detail'),
    
    # Region statistics and search
    path('worlds/<int:world_id>/regions/<int:region_id>/statistics/', viewregion.region_statistics, name='region_statistics'),
    path('worlds/<int:world_id>/regions/search/', viewregion.region_search, name='region_search'),
] 