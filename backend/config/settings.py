"""
Django settings for arcanovi project.

⚠️ ALLE Konfigurationswerte kommen aus der zentralen .env Datei!
⚠️ KEINE hardcoded Werte oder Fallbacks verwenden!
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =====================================================================================
# 🔐 SECURITY CONFIGURATION - AUS .env
# =====================================================================================
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']  # ⚠️ AUS .env: SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'  # ⚠️ AUS .env: DEBUG

# Allowed hosts - ⚠️ AUS .env: ALLOWED_HOSTS
ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')

# =====================================================================================
# 📦 APPLICATION DEFINITION
# =====================================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    # Core Apps
    'apps.core_user',
    'apps.permissions',
    'apps.characters',
    # Feature Apps - temporarily commented out for migration
    # 'apps.dungeon_master',
    'apps.world',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# =====================================================================================
# 🗄️ DATABASE CONFIGURATION - AUS .env
# =====================================================================================
# PostgreSQL als einzige Datenbank - ⚠️ ALLE Werte AUS .env!
DATABASES = {
    'default': {
        'ENGINE': os.environ['DATABASE_ENGINE'],        # ⚠️ AUS .env: DATABASE_ENGINE
        'NAME': os.environ['DATABASE_NAME'],            # ⚠️ AUS .env: DATABASE_NAME
        'USER': os.environ['DATABASE_USER'],            # ⚠️ AUS .env: DATABASE_USER
        'PASSWORD': os.environ['DATABASE_PASSWORD'],    # ⚠️ AUS .env: DATABASE_PASSWORD
        'HOST': os.environ['DATABASE_HOST'],            # ⚠️ AUS .env: DATABASE_HOST
        'PORT': os.environ['DATABASE_PORT'],            # ⚠️ AUS .env: DATABASE_PORT
        'CONN_MAX_AGE': int(os.environ.get('DATABASE_CONNECT_TIMEOUT', '10')),
    }
}

# =====================================================================================
# 🔒 PASSWORD VALIDATION
# =====================================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =====================================================================================
# 👤 AUTHENTICATION CONFIGURATION
# =====================================================================================
# Custom user model for Arcanovi
AUTH_USER_MODEL = 'core_user.User'

# =====================================================================================
# 🌍 INTERNATIONALIZATION - AUS .env
# =====================================================================================
LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'de-de')  # ⚠️ AUS .env: LANGUAGE_CODE
TIME_ZONE = os.environ.get('TIME_ZONE', 'Europe/Berlin')  # ⚠️ AUS .env: TIME_ZONE
USE_I18N = os.environ.get('USE_I18N', 'true').lower() == 'true'  # ⚠️ AUS .env: USE_I18N
USE_TZ = os.environ.get('USE_TZ', 'true').lower() == 'true'      # ⚠️ AUS .env: USE_TZ

# =====================================================================================
# 📁 STATIC FILES CONFIGURATION - AUS .env
# =====================================================================================
STATIC_URL = os.environ.get('STATIC_URL', '/static/')      # ⚠️ AUS .env: STATIC_URL
STATIC_ROOT = os.environ.get('STATIC_ROOT', '/app/staticfiles')  # ⚠️ AUS .env: STATIC_ROOT

# WhiteNoise Storage - ⚠️ AUS .env: STATICFILES_STORAGE
STATICFILES_STORAGE = os.environ.get('STATICFILES_STORAGE', 'whitenoise.storage.CompressedManifestStaticFilesStorage')

# =====================================================================================
# 🖼️ MEDIA FILES CONFIGURATION - AUS .env
# =====================================================================================
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')        # ⚠️ AUS .env: MEDIA_URL
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', '/app/media')   # ⚠️ AUS .env: MEDIA_ROOT

# =====================================================================================
# 🎛️ DJANGO REST FRAMEWORK - AUS .env
# =====================================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        os.environ.get('DRF_DEFAULT_PERMISSION', 'rest_framework.permissions.IsAuthenticated'),
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': int(os.environ.get('DRF_PAGE_SIZE', '20'))  # ⚠️ AUS .env: DRF_PAGE_SIZE
}

# =====================================================================================
# 🔐 JWT CONFIGURATION
# =====================================================================================
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# =====================================================================================
# 🌐 CORS CONFIGURATION - AUS .env
# =====================================================================================
# CORS Origins - ⚠️ AUS .env: CORS_ALLOWED_ORIGINS
CORS_ALLOWED_ORIGINS = os.environ['CORS_ALLOWED_ORIGINS'].split(',')

# CORS Credentials - ⚠️ AUS .env: CORS_ALLOW_CREDENTIALS
CORS_ALLOW_CREDENTIALS = os.environ.get('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true'

# CORS Allow All Origins - ⚠️ AUS .env: CORS_ALLOW_ALL_ORIGINS
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'false').lower() == 'true'

# =====================================================================================
# 🛡️ CSRF CONFIGURATION - AUS .env
# =====================================================================================
# CSRF Trusted Origins - ⚠️ AUS .env: CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = os.environ['CSRF_TRUSTED_ORIGINS'].split(',')

# =====================================================================================
# 📧 EMAIL CONFIGURATION - AUS .env
# =====================================================================================
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'false').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@arcanovi.com')

# =====================================================================================
# 🔐 SECURITY SETTINGS - AUS .env
# =====================================================================================
# Session Configuration
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'true').lower() == 'true'
SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')

# CSRF Configuration
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'false').lower() == 'true'
CSRF_COOKIE_HTTPONLY = os.environ.get('CSRF_COOKIE_HTTPONLY', 'false').lower() == 'true'
CSRF_COOKIE_SAMESITE = os.environ.get('CSRF_COOKIE_SAMESITE', 'Lax')

# HTTPS Configuration
USE_HTTPS = os.environ.get('USE_HTTPS', 'false').lower() == 'true'
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'false').lower() == 'true'

# =====================================================================================
# 🎮 ARCANOVI SPECIFIC SETTINGS - AUS .env
# =====================================================================================
# Arcanovi-spezifische Konfiguration
ARCANOVI_AUTO_SETUP = os.environ.get('ARCANOVI_AUTO_SETUP', 'true').lower() == 'true'
ARCANOVI_THEME = os.environ.get('ARCANOVI_THEME', 'fantasy')
ARCANOVI_DEFAULT_LANGUAGE = os.environ.get('ARCANOVI_DEFAULT_LANGUAGE', 'de')

# =====================================================================================
# 🔧 DJANGO CONFIGURATION
# =====================================================================================
# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging Configuration - ⚠️ AUS .env: LOG_LEVEL
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
    },
} 