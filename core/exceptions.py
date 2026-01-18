"""
Core Exceptions
---------------
Custom exception classes and centralized exception handler.

Purpose:
- Standardize error responses
- Provide meaningful error messages
- Log errors appropriately
- Handle different exception types consistently
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler.
    
    Provides consistent error response format:
    {
        "error": "Error type",
        "message": "Human-readable message",
        "details": {...},
        "status_code": 400
    }
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Standardize error response format
        custom_response_data = {
            'error': exc.__class__.__name__,
            'message': str(exc),
            'status_code': response.status_code
        }
        
        # Add details if available
        if hasattr(exc, 'detail'):
            custom_response_data['details'] = response.data
        
        response.data = custom_response_data
        
        # Log errors
        if response.status_code >= 500:
            logger.error(f"Server error: {exc}", exc_info=True)
    else:
        # Handle non-DRF exceptions
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        response = Response(
            {
                'error': 'ServerError',
                'message': 'An unexpected error occurred',
                'status_code': 500
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response


# Custom Exception Classes

class BusinessLogicError(Exception):
    """
    Base exception for business logic errors.
    """
    pass


class PaymentError(BusinessLogicError):
    """
    Payment-related errors.
    """
    pass


class OrderError(BusinessLogicError):
    """
    Order-related errors.
    """
    pass


class InventoryError(BusinessLogicError):
    """
    Inventory/stock-related errors.
    """
    pass


class ValidationError(BusinessLogicError):
    """
    Custom validation error.
    """
    pass


class AuthenticationError(BusinessLogicError):
    """
    Authentication-related errors.
    """
    pass


class PermissionDeniedError(BusinessLogicError):
    """
    Permission-related errors.
    """
    pass
