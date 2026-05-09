"""Middleware to bypass ALLOWED_HOSTS validation for healthcheck endpoint."""
from django.http import JsonResponse


class HealthCheckMiddleware:
    """Allow healthcheck requests to bypass ALLOWED_HOSTS and other validations."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # If this is a healthcheck request, return 200 immediately
        # without passing through Django's CommonMiddleware host validation
        if request.path == '/healthz':
            return JsonResponse({'status': 'ok'}, status=200)
        
        response = self.get_response(request)
        return response

