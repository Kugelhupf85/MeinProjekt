"""
URL configuration for Core User API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.user_views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 