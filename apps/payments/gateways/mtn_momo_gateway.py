"""
MTN Mobile Money Gateway
------------------------
Integration with MTN MoMo payment system.

MTN MoMo is ideal for:
- East African markets (Uganda, Rwanda, etc.)
- Mobile money payments
- Unbanked populations
- Direct mobile payments

Documentation: https://momodeveloper.mtn.com/
"""
import requests
import uuid
from django.conf import settings
from .base_gateway import BaseGateway, PaymentGatewayError
from typing import Dict, Any, Optional


class MTNMoMoGateway(BaseGateway):
    """
    MTN Mobile Money gateway implementation.
    
    Popular in Uganda, Rwanda, Ghana, and other African markets.
    """
    
    # Sandbox/Production URLs
    SANDBOX_URL = "https://sandbox.momodeveloper.mtn.com"
    PRODUCTION_URL = "https://proxy.momodeveloper.mtn.com"
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        self.is_sandbox = self.config.get('sandbox', True)
        self.base_url = self.SANDBOX_URL if self.is_sandbox else self.PRODUCTION_URL
        
        self.subscription_key = self.config.get('subscription_key', '')
        self.api_user = self.config.get('api_user', '')
        self.api_key = self.config.get('api_key', '')
    
    def _validate_config(self):
        required = ['subscription_key', 'api_user', 'api_key']
        
        for key in required:
            if not self.config.get(key):
                raise PaymentGatewayError(f"MTN MoMo {key} not configured")
    
    def _get_access_token(self):
        """
        Get OAuth access token for MTN MoMo API.
        """
        # Implementation for getting access token
        pass
    
    def initialize_payment(self, amount: float, currency: str, 
                          customer_email: str, metadata: Dict[str, Any]) -> Dict:
        """
        Initialize MTN MoMo payment request.
        
        For MoMo, this is typically a request to pay.
        """
        try:
            # MTN MoMo uses phone numbers, not emails
            phone_number = metadata.get('phone_number')
            
            if not phone_number:
                raise PaymentGatewayError("Phone number required for MTN MoMo")
            
            reference_id = str(uuid.uuid4())
            
            payload = {
                'amount': str(amount),
                'currency': currency.upper(),
                'externalId': metadata.get('order_id', reference_id),
                'payer': {
                    'partyIdType': 'MSISDN',
                    'partyId': phone_number
                },
                'payerMessage': 'Payment for order',
                'payeeNote': 'Order payment'
            }
            
            # Request to pay
            headers = {
                'X-Reference-Id': reference_id,
                'X-Target-Environment': 'sandbox' if self.is_sandbox else 'production',
                'Ocp-Apim-Subscription-Key': self.subscription_key,
                'Authorization': f'Bearer {self._get_access_token()}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'{self.base_url}/collection/v1_0/requesttopay',
                json=payload,
                headers=headers
            )
            
            if response.status_code != 202:
                raise PaymentGatewayError("MTN MoMo request failed")
            
            return {
                'transaction_id': reference_id,
                'reference': reference_id,
                'status': 'pending',
                'raw_response': {'reference_id': reference_id}
            }
            
        except requests.RequestException as e:
            raise PaymentGatewayError(f"MTN MoMo connection error: {str(e)}")
    
    def verify_payment(self, transaction_reference: str) -> Dict:
        """
        Verify MTN MoMo payment status.
        """
        try:
            headers = {
                'X-Target-Environment': 'sandbox' if self.is_sandbox else 'production',
                'Ocp-Apim-Subscription-Key': self.subscription_key,
                'Authorization': f'Bearer {self._get_access_token()}'
            }
            
            response = requests.get(
                f'{self.base_url}/collection/v1_0/requesttopay/{transaction_reference}',
                headers=headers
            )
            
            data = response.json()
            
            status_map = {
                'SUCCESSFUL': 'success',
                'FAILED': 'failed',
                'PENDING': 'pending'
            }
            
            return {
                'status': status_map.get(data['status'], 'pending'),
                'amount': float(data.get('amount', 0)),
                'currency': data.get('currency'),
                'transaction_id': transaction_reference,
                'paid_at': None,
                'raw_response': data
            }
            
        except requests.RequestException as e:
            raise PaymentGatewayError(f"MTN MoMo verification error: {str(e)}")
    
    def process_refund(self, transaction_id: str, 
                       amount: Optional[float] = None,
                       reason: str = '') -> Dict:
        """
        MTN MoMo refunds are typically handled manually.
        """
        raise NotImplementedError("MTN MoMo refunds handled manually")
    
    def verify_webhook_signature(self, payload: bytes, 
                                 signature: str) -> bool:
        """
        MTN MoMo webhook verification.
        """
        # Implementation depends on MTN's webhook setup
        return True
    
    def parse_webhook_event(self, payload: Dict) -> Dict:
        """
        Parse MTN MoMo webhook event.
        """
        return {
            'event_type': payload.get('status'),
            'transaction_id': payload.get('referenceId'),
            'reference': payload.get('referenceId'),
            'status': payload.get('status'),
            'amount': float(payload.get('amount', 0)),
            'currency': payload.get('currency'),
            'raw_data': payload
        }
    
    def get_supported_currencies(self) -> list:
        return ['UGX', 'GHS', 'XAF', 'ZMW']
    
    def get_supported_payment_methods(self) -> list:
        return ['mobile_money']
