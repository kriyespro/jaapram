"""
API application settings module.
This is used when running the API on its own server (port 8002).
"""

from ..base import *  # noqa

# API-specific settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Ram Naam Jaap API',
    'DESCRIPTION': 'API for Ram Naam Jaap application',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# API-specific installed apps
INSTALLED_APPS += [
    'drf_spectacular',
    'rest_framework.authtoken',
]

# API-specific middleware
MIDDLEWARE += [
    'corsheaders.middleware.CorsMiddleware',
]

# CORS settings
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://ramjaap.in',
]

CORS_ALLOW_CREDENTIALS = True

# Allow API to run on a different port
ALLOWED_HOSTS += ['api.ramjaap.in']

# API-specific static file settings
STATIC_URL = '/static/api/'

# Use a different database connection for API to optimize for read/write performance
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('API_DATABASE_URL', DATABASE_URL),
        conn_max_age=600,
    )
}

# Set session cookie name to avoid conflicts with other instances
SESSION_COOKIE_NAME = 'api_sessionid' 