from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.core.cache import cache

class InvalidURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:  # Check if the response status is 404 (Page Not Found)
            # Redirect to your specific page
            return HttpResponseRedirect(reverse('home'))  # 'invalid-url-page' should be replaced with the name of your URL pattern for the specific page
        return response

class LoginAttemptMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path != reverse('lockout_timer'):  # Allow access to the lockout timer view
            ip = self.get_client_ip(request)
            if ip:
                key = f'failed_login_attempts_{ip}'
                attempts, first_attempt_time = cache.get(key, (0, None))
                if attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                    lockout_time = settings.FAILED_LOGIN_LOCK_DURATION - (timezone.now() - first_attempt_time).total_seconds()
                    if lockout_time > 0:
                        return redirect('lockout_timer')
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip