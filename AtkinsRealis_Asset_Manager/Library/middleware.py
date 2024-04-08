from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponseRedirect

class InvalidURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:  # Check if the response status is 404 (Page Not Found)
            # Redirect to your specific page
            return HttpResponseRedirect(reverse('home'))  # 'invalid-url-page' should be replaced with the name of your URL pattern for the specific page
        return response