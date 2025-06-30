"""
URL configuration for Adventure campaign management endpoints.
"""
from django.urls import path
from ..endpoints.viewcampaign import (
    create_adventure,
    get_adventure,
    list_my_adventures,
    list_public_adventures,
    update_adventure,
    update_adventure_status,
    delete_adventure,
)

urlpatterns = [
    # Create new Adventure
    path('create/', create_adventure, name='create_adventure'),
    
    # List Adventures
    path('my/', list_my_adventures, name='list_my_adventures'),
    path('public/', list_public_adventures, name='list_public_adventures'),
    
    # Adventure CRUD operations
    path('<str:entity_id>/', get_adventure, name='get_adventure'),
    path('<str:entity_id>/update/', update_adventure, name='update_adventure'),
    path('<str:entity_id>/status/', update_adventure_status, name='update_adventure_status'),
    path('<str:entity_id>/delete/', delete_adventure, name='delete_adventure'),
] 