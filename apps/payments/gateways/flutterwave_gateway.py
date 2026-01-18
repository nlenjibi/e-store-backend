"""
Flutterwave Payment Gateway
---------------------------
Integration with Flutterwave payment processor.

Flutterwave is ideal for:
- Pan-African payments
- Multiple African countries
- Mobile money
- Bank transfers
- International cards

Documentation: https://developer.flutterwave.com/docs
"""
import requests
import hashlib
from django.conf import settings
from .base_gateway import BaseGateway, PaymentGatewayError
from typing import Dict, Any, Optional


class FlutterwaveGateway(BaseGateway):
    """
    Flutterwave payment gateway implementation.
    
    Covers wider African market than Paystack.
    """
    
    BASE_URL = "https://api.flutterwave.com/v3"
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        self.secret_key = (self.config.get('secret_key') or 
                          settings.FLUTTERWAVE_SECRET_KEY)
        
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def _validate_config(self):
        secret_key = self.config.get('secret_key') or getattr(settings, 'FLUTTERWAVE_SECRET_KEY', None)
        
        if not secret_key:
            raise PaymentGatewayError("Flutterwave secret key not configured")
    
    def initialize_payment(self, amount: float, currency: str, 
                          customer_email: str, metadata: Dict[str, Any]) -> Dict:
        """
        Initialize Flutterwave payment.
        """
        try:
            import uuid
            
            payload = {
                'tx_ref': str(uuid.uuid4()),
                'amount': amount,
                'currency': currency.upper(),
                'payment_options': 'card,mobilemoney,ussd',
                'customer': {
                    'email': customer_email
                },
                'meta': metadata,
                'customizations': {
                    'title': 'Payment',
                    'description': 'Order payment'
                }
            }
            
            response = requests.post(
                f'{self.BASE_URL}/payments',
                json=payload,
                headers=self.headers
            )
            
            data = response.json()
            
            if data.get('status') != 'success':
                raise PaymentGatewayError(data.get('message', 'Initialization failed'))
            
            result = data['data']
            
            return {
                'transaction_id': result['id'],
                'payment_url': result['link'],
                'reference': payload['tx_ref'],
                'status': 'pending',
                'raw_response': data
            }
            
        except requests.RequestException as e:
            raise PaymentGatewayError(f"Flutterwave connection error: {str(e)}")
    
    def verify_payment(self, transaction_reference: str) -> Dict:
        """
        Verify Flutterwave payment.
        """
        try:
            response = requests.get(
                f'{self.BASE_URL}/transactions/verify_by_reference',
                params={'tx_ref': transaction_reference},
                headers=self.headers
            )
            
            data = response.json()
            
            if data.get('status') != 'success':
                raise PaymentGatewayError(data.get('message', 'Verification failed'))
            
            result = data['data']
            
            status_map = {
                'successful': 'success',
                'failed': 'failed',
                'pending': 'pending'
            }
            
            return {
                'status': status_map.get(result['status'], 'pending'),
                'amount': result['amount'],
                'currency': result['currency'],
                'transaction_id': result['id'],
                'paid_at': result.get('created_at'),
                'raw_response': data
            }
            
        except requests.RequestException as e:
            raise PaymentGatewayError(f"Flutterwave verification error: {str(e)}")
    
    def process_refund(self, transaction_id: str, 
                       amount: Optional[float] = None,
                       reason: str = '') -> Dict:
        """
        Process Flutterwave refund.
        """
        # Flutterwave refund implementation
        pass
    
    def verify_webhook_signature(self, payload: bytes, 
                                 signature: str) -> bool:
        """
        Verify Flutterwave webhook signature.
        """
        computed_hash = hashlib.sha256(
            self.secret_key.encode('utf-8')
        ).hexdigest()
        
        return signature == computed_hash
    
    def parse_webhook_event(self, payload: Dict) -> Dict:
        """
        Parse Flutterwave webhook event.
        """
        event_type = payload.get('event', '')
        data = payload.get('data', {})
        
        return {
            'event_type': event_type,
            'transaction_id': data.get('id'),
            'reference': data.get('tx_ref'),
            'status': data.get('status'),
            'amount': data.get('amount'),
            'currency': data.get('currency'),
            'raw_data': payload
        }
    
    def get_supported_currencies(self) -> list:
        return ['NGN', 'GHS', 'KES', 'UGX', 'ZAR', 'USD', 'EUR', 'GBP']
    
    def get_supported_payment_methods(self) -> list:
        return ['card', 'mobile_money', 'bank_transfer', 'ussd']
