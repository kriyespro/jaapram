"""
Community application settings module.
This is used when running the community app on its own server (port 8004).
"""

from ..base import *  # noqa

# Community-specific installed apps
INSTALLED_APPS += [
    'channels',
    'django_filters',
]

# Channel layers for real-time chat
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [os.environ.get('REDIS_URL', 'redis://localhost:6379/3')],
        },
    },
}

# WebSocket ASGI application
ASGI_APPLICATION = 'ram_naam_jaap.config.asgi.application'

# Allow community to run on a different port/domain
ALLOWED_HOSTS += ['community.ramjaap.in']

# Community-specific static file settings
STATIC_URL = '/static/community/'

# Community-specific middleware
MIDDLEWARE += [
    'ram_naam_jaap.community.middleware.CommunityTrackingMiddleware',
]

# Community settings
COMMUNITY_POSTS_PER_PAGE = 15
COMMUNITY_COMMENTS_PER_PAGE = 20
COMMUNITY_MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

# Use a different database connection for community to optimize for real-time performance
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('COMMUNITY_DATABASE_URL', DATABASE_URL),
        conn_max_age=600,
    )
}

# Redis cache for community real-time features
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/3'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 300,  # 5 minutes
    }
}

# Set session cookie name to avoid conflicts with other instances
SESSION_COOKIE_NAME = 'community_sessionid'

# Customize templates for community
TEMPLATES[0]['DIRS'] = [
    os.path.join(BASE_DIR, 'templates/community'),
    os.path.join(BASE_DIR, 'templates'),
] 