"""
WSGI config for dungeonmaster project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dungeonmaster.settings')

application = get_wsgi_application() 