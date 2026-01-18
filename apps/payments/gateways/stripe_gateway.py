"""
Stripe Payment Gateway
----------------------
Integration with Stripe payment processor.

Stripe is ideal for:
- Global payments
- Credit/debit cards
- Digital wallets (Apple Pay, Google Pay)
- Subscriptions
- US/European markets

Documentation: https://stripe.com/docs/api
"""
import stripe
from django.conf import settings
from .base_gateway import BaseGateway, PaymentGatewayError
from typing import Dict, Any, Optional


class StripeGateway(BaseGateway):
    """
    Stripe payment gateway implementation.
    
    Uses Stripe's Payment Intents API for SCA compliance.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Stripe gateway.
        
        Config should contain:
        - secret_key: Stripe secret key
        - publishable_key: Stripe publishable key
        - webhook_secret: Webhook signing secret
        """
        super().__init__(config)
        
        # Set Stripe API key
        stripe.api_key = self.config.get('secret_key') or settings.STRIPE_SECRET_KEY
    
    def _validate_config(self):
        """
        Validate Stripe configuration.
        """
        secret_key = self.config.get('secret_key') or getattr(settings, 'STRIPE_SECRET_KEY', None)
        
        if not secret_key:
            raise PaymentGatewayError("Stripe secret key not configured")
    
    def initialize_payment(self, amount: float, currency: str, 
                          customer_email: str, metadata: Dict[str, Any]) -> Dict:
        """
        Create a Stripe Payment Intent.
        
        Stripe amounts are in cents/smallest currency unit.
        """
        try:
            # Convert to cents
            amount_cents = int(amount * 100)
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                receipt_email=customer_email,
                metadata=metadata,
                automatic_payment_methods={'enabled': True},
            )
            
            return {
                'transaction_id': intent.id,
                'client_secret': intent.client_secret,
                'status': intent.status,
                'reference': intent.id,
                'raw_response': intent
            }
            
        except stripe.error.StripeError as e:
            raise PaymentGatewayError(f"Stripe error: {str(e)}")
    
    def verify_payment(self, transaction_reference: str) -> Dict:
        """
        Verify payment status with Stripe.
        """
        try:
            intent = stripe.PaymentIntent.retrieve(transaction_reference)
            
            status_map = {
                'succeeded': 'success',
                'processing': 'pending',
                'requires_payment_method': 'failed',
                'requires_confirmation': 'pending',
                'requires_action': 'pending',
                'canceled': 'failed',
            }
            
            return {
                'status': status_map.get(intent.status, 'pending'),
                'amount': intent.amount / 100,  # Convert from cents
                'currency': intent.currency.upper(),
                'transaction_id': intent.id,
                'paid_at': intent.created if intent.status == 'succeeded' else None,
                'raw_response': intent
            }
            
        except stripe.error.StripeError as e:
            raise PaymentGatewayError(f"Stripe verification error: {str(e)}")
    
    def process_refund(self, transaction_id: str, 
                       amount: Optional[float] = None,
                       reason: str = '') -> Dict:
        """
        Process Stripe refund.
        """
        try:
            refund_data = {'payment_intent': transaction_id}
            
            if amount:
                refund_data['amount'] = int(amount * 100)  # Convert to cents
            
            if reason:
                refund_data['reason'] = reason
            
            refund = stripe.Refund.create(**refund_data)
            
            return {
                'refund_id': refund.id,
                'status': refund.status,
                'amount': refund.amount / 100,
                'raw_response': refund
            }
            
        except stripe.error.StripeError as e:
            raise PaymentGatewayError(f"Stripe refund error: {str(e)}")
    
    def verify_webhook_signature(self, payload: bytes, 
                                 signature: str) -> bool:
        """
        Verify Stripe webhook signature.
        """
        webhook_secret = (self.config.get('webhook_secret') or 
                         settings.STRIPE_WEBHOOK_SECRET)
        
        try:
            stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return True
        except Exception:
            return False
    
    def parse_webhook_event(self, payload: Dict) -> Dict:
        """
        Parse Stripe webhook event.
        """
        event_type = payload.get('type', '')
        data = payload.get('data', {}).get('object', {})
        
        event_map = {
            'payment_intent.succeeded': 'payment.success',
            'payment_intent.payment_failed': 'payment.failed',
            'charge.refunded': 'refund.completed',
        }
        
        return {
            'event_type': event_map.get(event_type, event_type),
            'transaction_id': data.get('id'),
            'reference': data.get('id'),
            'status': data.get('status'),
            'amount': data.get('amount', 0) / 100,
            'currency': data.get('currency', '').upper(),
            'raw_data': payload
        }
    
    def get_supported_currencies(self) -> list:
        """
        Stripe supports 135+ currencies.
        """
        return ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'NGN', 'ZAR', 'KES', 'GHS']
    
    def get_supported_payment_methods(self) -> list:
        """
        Stripe payment methods.
        """
        return ['card', 'apple_pay', 'google_pay', 'bank_transfer']
