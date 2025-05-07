"""
Admin application settings module.
This is used when running the admin app on its own server (port 8001).
"""

from ..base import *  # noqa

# Use a different database connection for admin to reduce load on the main DB
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('ADMIN_DATABASE_URL', DATABASE_URL),
        conn_max_age=600,
    )
}

# Custom admin-specific middleware
MIDDLEWARE += [
    'ram_naam_jaap.core.middleware.AdminAccessMiddleware',
]

# Allow admin site to run on a different port
ALLOWED_HOSTS += ['admin.ramjaap.in']

# Admin site specific settings
ADMIN_SITE_HEADER = "Ram Naam Jaap Administration"
ADMIN_SITE_TITLE = "Ram Naam Jaap Admin Portal"

# Increase cache timeout for admin site
CACHES['default']['TIMEOUT'] = 60 * 60  # 1 hour

# Admin-specific static file settings
STATIC_URL = '/static/admin/'

# Set session cookie name to avoid conflicts with other instances
SESSION_COOKIE_NAME = 'admin_sessionid' 