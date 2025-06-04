from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Character, Campaign


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class CharacterSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Character
        fields = '__all__'


class CampaignSerializer(serializers.ModelSerializer):
    dungeon_master = UserSerializer(read_only=True)
    players = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Campaign
        fields = '__all__' 