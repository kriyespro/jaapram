"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

# Custom admin site settings
admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_INDEX_TITLE

urlpatterns = [
    # Django admin using custom URL from settings
    path(f'{settings.ADMIN_URL}', admin.site.urls),
    
    # Custom dashboard at /admin
    path(f'{settings.DASHBOARD_URL}', include('core.dashboard_urls')),
    
    # Apps URLs
    path('', include('core.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),  # Custom accounts URLs
    path('jaap/', include('jaap.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('community/', include('community.urls')),
]

# Media URLs in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
