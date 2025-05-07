from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# CORS in development
CORS_ALLOW_ALL_ORIGINS = True

# Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar - already included in INSTALLED_APPS and MIDDLEWARE from base.py
INTERNAL_IPS = ['127.0.0.1']

# Make debug toolbar work with docker
if os.environ.get('USE_DOCKER') == 'yes':
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += ['.'.join(ip.split('.')[:-1] + ['1']) for ip in ips]

# Tailwind Development Mode
TAILWIND_DEV_MODE = True
