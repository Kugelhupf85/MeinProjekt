"""
Character API URLs
URL configuration for character management endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.characters.api.views.character_views import (
    CharacterViewSet, RuleSetViewSet, DSARaceViewSet, DSACultureViewSet,
    DSAProfessionViewSet, DSAAdvantageViewSet, DSADisadvantageViewSet,
    ReferenceDataViewSet
)

# Router für ViewSets
router = DefaultRouter()
router.register(r'characters', CharacterViewSet, basename='character')
router.register(r'rulesets', RuleSetViewSet, basename='ruleset')
router.register(r'races', DSARaceViewSet, basename='dsa-race')
router.register(r'cultures', DSACultureViewSet, basename='dsa-culture')
router.register(r'professions', DSAProfessionViewSet, basename='dsa-profession')
router.register(r'advantages', DSAAdvantageViewSet, basename='dsa-advantage')
router.register(r'disadvantages', DSADisadvantageViewSet, basename='dsa-disadvantage')
router.register(r'reference', ReferenceDataViewSet, basename='reference-data')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
] 