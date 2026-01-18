"""Custom middleware for the Smart E-Commerce platform."""
import json
import time
import logging
import hashlib
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.utils.cache import patch_cache_control, patch_vary_headers

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware to log API requests for analytics and debugging."""
    
    def process_request(self, request):
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        if hasattr(request, 'start_time') and request.path.startswith('/api/'):
            duration = time.time() - request.start_time
            
            # Log request details
            log_data = {
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
                'status_code': response.status_code,
                'duration': f"{duration:.3f}s",
            }
            
            # Log to Django logger
            logger.info(f"API Request: {log_data['method']} {log_data['path']} - {log_data['status_code']} ({log_data['duration']})")
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """Middleware to implement rate limiting."""
    
    def process_request(self, request):
        # Implement rate limiting logic here
        # This is a simplified version - in production, use django-ratelimit
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware to add security headers to responses."""
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class CacheControlMiddleware(MiddlewareMixin):
    """
    Intelligent cache control middleware for API responses.
    
    Features:
    - Adds appropriate Cache-Control headers
    - Generates ETags for GET requests
    - Handles 304 Not Modified responses
    - Varies cache by Authorization header for user-specific content
    - Never caches sensitive endpoints (cart, payments, auth)
    """
    
    # Endpoints that should NEVER be cached
    NEVER_CACHE_PATHS = [
        '/api/cart/',
        '/api/checkout/',
        '/api/payments/',
        '/api/webhooks/',
        '/api/auth/',
        '/api/user/',
        '/admin/',
    ]
    
    # Endpoints with specific cache durations (in seconds)
    CACHE_DURATIONS = {
        '/api/products/': 600,          # 10 minutes
        '/api/categories/': 900,        # 15 minutes
        '/api/promotions/': 300,        # 5 minutes
        '/api/homepage/': 300,          # 5 minutes
        '/api/analytics/public/': 600,  # 10 minutes
    }
    
    def _should_never_cache(self, path: str) -> bool:
        """Check if path should never be cached"""
        return any(path.startswith(never_cache) for never_cache in self.NEVER_CACHE_PATHS)
    
    def _get_cache_duration(self, path: str) -> int:
        """Get cache duration for path"""
        for cache_path, duration in self.CACHE_DURATIONS.items():
            if path.startswith(cache_path):
                return duration
        return 0
    
    def _generate_etag(self, content: bytes) -> str:
        """Generate ETag from response content"""
        return hashlib.md5(content).hexdigest()
    
    def process_response(self, request, response):
        """Add cache headers and handle ETags"""
        
        # Only process successful GET requests
        if request.method != 'GET' or response.status_code != 200:
            return response
        
        path = request.path
        
        # Never cache sensitive endpoints
        if self._should_never_cache(path):
            patch_cache_control(response, no_cache=True, no_store=True, must_revalidate=True, private=True)
            response['Pragma'] = 'no-cache'
            return response
        
        # Get cache duration for this endpoint
        cache_duration = self._get_cache_duration(path)
        
        if cache_duration > 0:
            # Public endpoints - can be cached by CDN/browser
            if request.user.is_authenticated:
                # User-specific content - private cache
                patch_cache_control(response, private=True, max_age=cache_duration)
                # Vary by Authorization to prevent serving user A's cached data to user B
                patch_vary_headers(response, ['Authorization', 'Cookie'])
            else:
                # Public content - can be cached by CDN
                patch_cache_control(response, public=True, max_age=cache_duration, s_maxage=cache_duration)
                patch_vary_headers(response, ['Accept-Encoding', 'Accept-Language'])
            
            # Generate ETag for conditional requests
            if hasattr(response, 'content') and response.content:
                etag = self._generate_etag(response.content)
                response['ETag'] = f'"{etag}"'
                
                # Check If-None-Match header for conditional request
                if_none_match = request.META.get('HTTP_IF_NONE_MATCH')
                if if_none_match:
                    # Remove quotes from If-None-Match
                    client_etag = if_none_match.strip('"')
                    if client_etag == etag:
                        # Content hasn't changed - return 304
                        response.status_code = 304
                        response.content = b''
                        logger.debug(f"ETag match - returning 304 for {path}")
        else:
            # No specific cache policy - default to no-cache for API
            if path.startswith('/api/'):
                patch_cache_control(response, no_cache=True, private=True, max_age=0)
        
        return response
