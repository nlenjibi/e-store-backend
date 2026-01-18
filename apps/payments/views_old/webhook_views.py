"""
Webhook Views
-------------
Handles incoming webhooks from payment gateways.

Responsibilities:
- Validate webhook signatures
- Parse webhook payloads
- Trigger appropriate payment updates
- Return proper HTTP responses

Security critical:
- Always verify webhook authenticity
- Log all webhook attempts
- Handle idempotency
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    Handle Stripe webhooks.
    """
    permission_classes = []  # Webhooks bypass normal auth
    
    def post(self, request):
        """
        Process Stripe webhook events.
        """
        # Verify signature, process event
        pass


@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(APIView):
    """
    Handle Paystack webhooks.
    """
    permission_classes = []
    
    def post(self, request):
        pass


@method_decorator(csrf_exempt, name='dispatch')
class FlutterwaveWebhookView(APIView):
    """
    Handle Flutterwave webhooks.
    """
    permission_classes = []
    
    def post(self, request):
        pass


@method_decorator(csrf_exempt, name='dispatch')
class MTNMoMoWebhookView(APIView):
    """
    Handle MTN MoMo webhooks.
    """
    permission_classes = []
    
    def post(self, request):
        pass
