"""
Core Renderers
--------------
Custom response renderers for consistent API formatting.

Purpose:
- Standardize API response format
- Add envelope/wrapper to responses
- Include metadata
"""
from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    """
    Custom JSON renderer with consistent envelope.
    
    Response format:
    {
        "success": true,
        "data": {...},
        "message": "Operation successful",
        "timestamp": "2026-01-04T10:00:00Z"
    }
    """
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Wrap response data in standard envelope.
        """
        from datetime import datetime
        
        response = renderer_context.get('response') if renderer_context else None
        
        # Don't wrap error responses (already handled by exception handler)
        if response and response.status_code >= 400:
            return super().render(data, accepted_media_type, renderer_context)
        
        # Wrap successful responses
        wrapped_data = {
            'success': True,
            'data': data,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Add message if available
        if response and hasattr(response, 'message'):
            wrapped_data['message'] = response.message
        
        return super().render(wrapped_data, accepted_media_type, renderer_context)
