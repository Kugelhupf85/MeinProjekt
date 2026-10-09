from django.apps import AppConfig


class AdventureConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.adventure'
    verbose_name = 'Adventure'
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        """
        from . import listeners 