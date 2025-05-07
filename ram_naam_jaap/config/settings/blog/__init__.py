"""
Blog application settings module.
This is used when running the blog app on its own server (port 8003).
"""

from ..base import *  # noqa

# Blog-specific installed apps
INSTALLED_APPS += [
    'taggit',
    'ckeditor',
    'ckeditor_uploader',
]

# CKEditor configuration
CKEDITOR_UPLOAD_PATH = "uploads/blog/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ],
        'height': 300,
        'width': '100%',
    },
}

# Allow blog to run on a different port/domain
ALLOWED_HOSTS += ['blog.ramjaap.in']

# Blog-specific static file settings
STATIC_URL = '/static/blog/'

# Blog-specific middleware
MIDDLEWARE += [
    'ram_naam_jaap.blog.middleware.BlogViewCountMiddleware',
]

# Blog pagination settings
BLOG_POSTS_PER_PAGE = 10
BLOG_RELATED_POSTS_LIMIT = 3

# Use a different database connection for blog to reduce load on the main DB
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('BLOG_DATABASE_URL', DATABASE_URL),
        conn_max_age=600,
    )
}

# Set session cookie name to avoid conflicts with other instances
SESSION_COOKIE_NAME = 'blog_sessionid'

# Customize templates for blog
TEMPLATES[0]['DIRS'] = [
    os.path.join(BASE_DIR, 'templates/blog'),
    os.path.join(BASE_DIR, 'templates'),
] 