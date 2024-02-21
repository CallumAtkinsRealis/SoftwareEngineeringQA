from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            # If not authenticated, redirect to the login page
            return redirect(reverse('login'))  # Assuming your login URL name is 'login'
        
        # If authenticated, continue with the request
        response = self.get_response(request)
        return response
    
class SessionExpiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is authenticated and the session has expired
        if request.user.is_authenticated and '_session_expiry' in request.session:
            session_expiry = request.session['_session_expiry']
            if session_expiry < timezone.now():
                # Session has expired, redirect to the login page
                return redirect(reverse('login'))  # Assuming your login URL name is 'login'
        
        response = self.get_response(request)
        return response