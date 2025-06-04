from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Character, Campaign
from .serializers import UserSerializer, CharacterSerializer, CampaignSerializer


@api_view(['GET'])
def api_overview(request):
    """API overview endpoint"""
    api_urls = {
        'API Overview': '/api/',
        'Characters': '/api/characters/',
        'Campaigns': '/api/campaigns/',
        'Users': '/api/users/',
        'Admin': '/admin/',
    }
    return Response(api_urls)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for users (read-only)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CharacterViewSet(viewsets.ModelViewSet):
    """ViewSet for characters"""
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CampaignViewSet(viewsets.ModelViewSet):
    """ViewSet for campaigns"""
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    
    def perform_create(self, serializer):
        serializer.save(dungeon_master=self.request.user) 