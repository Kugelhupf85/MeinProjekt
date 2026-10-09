"""
URL configuration for arcanovi project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Core User Management
    path('api/auth/', include('apps.core_user.urls')),
    # Temporarily commented out for migration
    # path('api/dungeon-master/', include('apps.dungeon_master.urls')),
    path('api/world/', include('apps.world.urls')),
    # Character Management
    path('api/', include('apps.characters.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 