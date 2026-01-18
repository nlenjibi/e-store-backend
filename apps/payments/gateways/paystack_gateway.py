"""
Paystack Payment Gateway
------------------------
Integration with Paystack payment processor.

Paystack is ideal for:
- African markets (Nigeria, Ghana, South Africa)
- Local payment methods
- Bank transfers
- USSD payments
- Mobile money

Documentation: https://paystack.com/docs/api
"""
import requests
import hashlib
import hmac
from django.conf import settings
from .base_gateway import BaseGateway, PaymentGatewayError
from typing import Dict, Any, Optional


class PaystackGateway(BaseGateway):
    """
    Paystack payment gateway implementation.
    
    Primary gateway for Nigerian, Ghanaian, and South African customers.
    """
    
    BASE_URL = "https://api.paystack.co"
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Paystack gateway.
        
        Config should contain:
        - secret_key: Paystack secret key
        """
        super().__init__(config)
        
        self.secret_key = (self.config.get('secret_key') or 
                          settings.PAYSTACK_SECRET_KEY)
        
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def _validate_config(self):
        """
        Validate Paystack configuration.
        """
        secret_key = self.config.get('secret_key') or getattr(settings, 'PAYSTACK_SECRET_KEY', None)
        
        if not secret_key:
            raise PaymentGatewayError("Paystack secret key not configured")
    
    def initialize_payment(self, amount: float, currency: str, 
                          customer_email: str, metadata: Dict[str, Any]) -> Dict:
        """
        Initialize Paystack transaction.
        
        Paystack amounts are in kobo (for NGN) or pesewas (for GHS).
        """
        try:
            # Convert to smallest unit (kobo/pesewas)
            amount_kobo = int(amount * 100)
            
            payload = {
                'email': customer_email,
                'amount': amount_kobo,
                'currency': currency.upper(),
                'metadata': metadata
            }
            
            response = requests.post(
                f'{self.BASE_URL}/transaction/initialize',
                json=payload,
                headers=self.headers
            )
            
            data = response.json()
            
            if not data.get('status'):
                raise PaymentGatewayError(data.get('message', 'Initialization failed'))
            
            result = data['data']
            
            return {
                'transaction_id': result['reference'],
                'payment_url': result['authorization_url'],
                'access_code': result['access_code'],
                'reference': result['reference'],
                'status': 'pending',
                'raw_response': data
            }
            
        except requests.RequestException as e:
            raise PaymentGatewayError(f"Paystack connection error: {str(e)}")
    
    def verify_payment(self, transaction_reference: str) -> Dict:
        """
        Verify payment with Paystack.
        """
        try:
            response = requests.get(
                f'{self.BASE_URL}/transaction/verify/{transaction_reference}',
                headers=self.headers
            )
            
            data = response.json()
            
            if not data.get('status'):
                raise PaymentGatewayError(data.get('message', 'Verification failed'))
            
            result = data['data']
            
            status_map = {
                'success': 'success',
                'failed': 'failed',
                'abandoned': 'failed',
                'pending': 'pending'
            }
            
            return {
                'status': status_map.get(result['status'], 'pending'),
                'amount': result['amount'] / 100,  # Convert from kobo
                'currency': result['currency'],
                'transaction_id': result['reference'],
                'paid_at': result.get('paid_at'),
                'raw_response': data
            }
            
        except requests.RequestException as e:
            raise PaymentGatewayError(f"Paystack verification error: {str(e)}")
    
    def process_refund(self, transaction_id: str, 
                       amount: Optional[float] = None,
                       reason: str = '') -> Dict:
        """
        Process Paystack refund.
        """
        try:
            payload = {
                'transaction': transaction_id
            }
            
            if amount:
                payload['amount'] = int(amount * 100)  # Convert to kobo
            
            response = requests.post(
                f'{self.BASE_URL}/refund',
                json=payload,
                headers=self.headers
            )
            
            data = response.json()
            
            if not data.get('status'):
                raise PaymentGatewayError(data.get('message', 'Refund failed'))
            
            result = data['data']
            
            return {
                'refund_id': result['id'],
                'status': result['status'],
                'amount': result.get('amount', 0) / 100,
                'raw_response': data
            }
            
        except requests.RequestException as e:
            raise PaymentGatewayError(f"Paystack refund error: {str(e)}")
    
    def verify_webhook_signature(self, payload: bytes, 
                                 signature: str) -> bool:
        """
        Verify Paystack webhook signature.
        """
        computed_signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(computed_signature, signature)
    
    def parse_webhook_event(self, payload: Dict) -> Dict:
        """
        Parse Paystack webhook event.
        """
        event_type = payload.get('event', '')
        data = payload.get('data', {})
        
        event_map = {
            'charge.success': 'payment.success',
            'charge.failed': 'payment.failed',
            'refund.processed': 'refund.completed',
        }
        
        return {
            'event_type': event_map.get(event_type, event_type),
            'transaction_id': data.get('reference'),
            'reference': data.get('reference'),
            'status': data.get('status'),
            'amount': data.get('amount', 0) / 100,
            'currency': data.get('currency'),
            'raw_data': payload
        }
    
    def get_supported_currencies(self) -> list:
        """
        Paystack supported currencies.
        """
        return ['NGN', 'GHS', 'ZAR', 'USD']
    
    def get_supported_payment_methods(self) -> list:
        """
        Paystack payment methods.
        """
        return ['card', 'bank', 'bank_transfer', 'ussd', 'mobile_money', 'qr']
