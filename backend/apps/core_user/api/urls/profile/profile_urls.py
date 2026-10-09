"""
Profile Management URL Configuration.
"""
from django.urls import path
from ...views.profile import (
    profile_view, update_profile_view, UserListView,
    user_detail_view, toggle_user_active_view
)

urlpatterns = [
    # Current User Profile
    path('profile/', profile_view, name='profile'),
    path('profile/update/', update_profile_view, name='update-profile'),
    
    # User Management (Admin)
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/', user_detail_view, name='user-detail'),
    path('users/<int:user_id>/toggle-active/', toggle_user_active_view, name='toggle-user-active'),
] 