from django.apps import AppConfig


class DungeonMasterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dungeon_master'
    verbose_name = 'Dungeon Master'
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        """
        from . import listeners 