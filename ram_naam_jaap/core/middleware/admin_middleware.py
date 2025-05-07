"""
Admin access middleware to restrict access to the admin application.
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


class AdminAccessMiddleware:
    """
    Middleware to ensure only staff/superuser accounts can access the admin interface.
    This is used in the admin-specific settings module and provides an additional 
    layer of security by enforcing admin access rights at the middleware level.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip this middleware for authentication URLs to allow login
        auth_urls = ['/login/', '/logout/', '/admin/login/', '/durga/login/']
        if any(request.path.startswith(url) for url in auth_urls):
            return self.get_response(request)

        # Check if the user is authenticated and is staff
        if not request.user.is_authenticated:
            messages.warning(request, "You must be logged in to access this area.")
            return redirect('account_login')
        
        # For non-staff trying to access any admin page
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this area.")
            # Redirect to home page or user dashboard
            return redirect('jaap:home')
            
        response = self.get_response(request)
        return response 