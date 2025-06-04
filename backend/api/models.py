from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    """Base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Character(BaseModel):
    """Example Character model for D&D"""
    name = models.CharField(max_length=100)
    character_class = models.CharField(max_length=50)
    level = models.IntegerField(default=1)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='characters')
    
    def __str__(self):
        return f"{self.name} ({self.character_class} Level {self.level})"


class Campaign(BaseModel):
    """Example Campaign model"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    dungeon_master = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dm_campaigns')
    players = models.ManyToManyField(User, related_name='player_campaigns', blank=True)
    
    def __str__(self):
        return self.name 