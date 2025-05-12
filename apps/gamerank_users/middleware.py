from django.shortcuts import redirect
from django.urls import reverse
from typing import Optional, Callable
from django.http import HttpRequest, HttpResponse


class CustomAuthMiddleware:
    """Middleware to handle custom password-based authentication."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Define public URLs inside the call method
        login_url = reverse('gamerank_users:login') # Use namespaced URL
        public_paths = [
            reverse('gamerank_core:home'), # Use namespaced URL
            login_url,
            '/static/',
            '/admin/', # Allow access to admin
            # Add other public paths like /media/ if needed
        ]

        # Check if the current path starts with any public path
        is_public_path = any(request.path.startswith(path) for path in public_paths)
        
        # If path is not public and user is not authenticated via session
        if not is_public_path and not request.session.get('auth'):
            # Redirect to login, passing the current path as next parameter
            return redirect(f'{login_url}?next={request.path}')

        return self.get_response(request) 