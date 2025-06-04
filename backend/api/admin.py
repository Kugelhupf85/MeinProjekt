from django.contrib import admin
from .models import Character, Campaign


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_class', 'level', 'owner', 'created_at']
    list_filter = ['character_class', 'level', 'created_at']
    search_fields = ['name', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'dungeon_master', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'dungeon_master__username']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['players'] 