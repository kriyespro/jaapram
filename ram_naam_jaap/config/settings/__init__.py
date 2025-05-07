import os

# Load settings based on environment
ENV = os.environ.get('DJANGO_ENV', 'local')

if ENV == 'production':
    from .production import *
else:
    from .local import *
