"""
Base Payment Gateway
--------------------
Abstract base class defining the payment gateway interface.

All payment gateways MUST implement this interface.
This ensures consistency and makes gateways interchangeable.

Why this matters:
- Switching gateways doesn't break code
- Testing is easier (mock gateways)
- New gateways follow same pattern
- Service layer doesn't care about implementation
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseGateway(ABC):
    """
    Abstract base class for payment gateways.
    
    All payment gateways must implement these methods.
    This contract ensures all gateways are interchangeable.
    
    Design Pattern: Template Method + Strategy
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize gateway with configuration.
        
        Args:
            config: Gateway-specific configuration (API keys, etc.)
        """
        self.config = config or {}
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self):
        """
        Validate that all required configuration is present.
        
        Raises:
            ValueError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    def initialize_payment(self, amount: float, currency: str, 
                          customer_email: str, metadata: Dict[str, Any]) -> Dict:
        """
        Initialize a payment transaction.
        
        This creates a payment intent/transaction on the gateway side.
        
        Args:
            amount: Payment amount
            currency: Currency code (e.g., 'USD', 'NGN')
            customer_email: Customer's email
            metadata: Additional transaction metadata (order_id, etc.)
        
        Returns:
            dict: {
                'transaction_id': str,
                'payment_url': str (if redirect needed),
                'reference': str,
                'status': str,
                'raw_response': dict (full gateway response)
            }
        
        Raises:
            PaymentGatewayError: If initialization fails
        """
        pass
    
    @abstractmethod
    def verify_payment(self, transaction_reference: str) -> Dict:
        """
        Verify a payment status with the gateway.
        
        Args:
            transaction_reference: Transaction reference from gateway
        
        Returns:
            dict: {
                'status': str ('success', 'pending', 'failed'),
                'amount': float,
                'currency': str,
                'transaction_id': str,
                'paid_at': datetime (if successful),
                'raw_response': dict
            }
        """
        pass
    
    @abstractmethod
    def process_refund(self, transaction_id: str, 
                       amount: Optional[float] = None,
                       reason: str = '') -> Dict:
        """
        Process a refund.
        
        Args:
            transaction_id: Original transaction ID
            amount: Refund amount (None for full refund)
            reason: Reason for refund
        
        Returns:
            dict: {
                'refund_id': str,
                'status': str,
                'amount': float,
                'raw_response': dict
            }
        """
        pass
    
    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, 
                                 signature: str) -> bool:
        """
        Verify webhook signature for security.
        
        Critical for security - ensures webhook is from gateway.
        
        Args:
            payload: Raw webhook payload
            signature: Signature from webhook headers
        
        Returns:
            bool: True if signature is valid
        """
        pass
    
    @abstractmethod
    def parse_webhook_event(self, payload: Dict) -> Dict:
        """
        Parse webhook payload into standardized format.
        
        Args:
            payload: Raw webhook payload
        
        Returns:
            dict: {
                'event_type': str ('payment.success', 'payment.failed', etc.),
                'transaction_id': str,
                'reference': str,
                'status': str,
                'amount': float,
                'currency': str,
                'raw_data': dict
            }
        """
        pass
    
    def get_supported_currencies(self) -> list:
        """
        Get list of currencies supported by this gateway.
        
        Returns:
            list: Currency codes
        """
        return []
    
    def get_supported_payment_methods(self) -> list:
        """
        Get list of payment methods supported by this gateway.
        
        Returns:
            list: Payment method identifiers
        """
        return []


class PaymentGatewayError(Exception):
    """
    Base exception for payment gateway errors.
    """
    pass


class GatewayConfigurationError(PaymentGatewayError):
    """
    Raised when gateway configuration is invalid.
    """
    pass


class GatewayConnectionError(PaymentGatewayError):
    """
    Raised when cannot connect to gateway.
    """
    pass


class PaymentVerificationError(PaymentGatewayError):
    """
    Raised when payment verification fails.
    """
    pass
