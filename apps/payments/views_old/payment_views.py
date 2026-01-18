"""
Payment Views
-------------
Handles core payment operations:
- Payment initiation
- Payment status checking
- Payment history retrieval
- Transaction listing

Keep views thin - delegate business logic to services.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for payment operations.
    
    Responsibilities:
    - Validate incoming requests
    - Call payment service methods
    - Return formatted responses
    - Handle HTTP-level concerns
    
    Does NOT:
    - Process payments directly
    - Interact with payment gateways
    - Contain business logic
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def initiate(self, request):
        """
        Initiate a new payment.
        Delegates to PaymentService.
        """
        # Implementation delegated to service layer
        pass
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """
        Check payment status.
        """
        pass
