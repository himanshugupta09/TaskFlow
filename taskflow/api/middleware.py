"""Middleware to bypass ALLOWED_HOSTS validation for healthcheck endpoint."""
from django.core.exceptions import DisallowedHost


class HealthCheckMiddleware:
    """Allow healthcheck requests to bypass ALLOWED_HOSTS validation."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Allow /healthz endpoint to bypass host validation
        if request.path == '/healthz':
            # Temporarily set a valid host to bypass validation
            request.META['HTTP_HOST'] = request.META.get('SERVER_NAME', 'localhost')
        
        try:
            response = self.get_response(request)
        except DisallowedHost:
            # If this is a healthcheck request, allow it anyway
            if request.path == '/healthz':
                from django.http import JsonResponse
                return JsonResponse({'status': 'ok'}, status=200)
            raise
        
        return response
