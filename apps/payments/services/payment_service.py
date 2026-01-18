"""
Payment Service
---------------
Core payment processing orchestration.

This is the heart of the payment system.

Responsibilities:
✓ Orchestrate payment flow
✓ Select appropriate gateway
✓ Handle payment state transitions
✓ Coordinate with order service
✓ Log all payment attempts
✓ Handle errors gracefully
✓ Ensure idempotency

Does NOT:
✗ Make direct API calls to gateways (use gateway classes)
✗ Handle webhooks (separate concern)
✗ Contain HTTP/view logic
"""


class PaymentService:
    """
    Main payment orchestration service.
    
    This service coordinates the entire payment flow:
    1. Validate payment request
    2. Check fraud score
    3. Select payment gateway
    4. Process payment
    5. Update order status
    6. Send notifications
    
    Usage:
        service = PaymentService()
        result = service.process_payment(order_id, payment_method, amount)
    """
    
    def __init__(self):
        """
        Initialize service with dependencies.
        """
        from .gateway_factory import GatewayFactory
        from .fraud_service import FraudService
        from .currency_service import CurrencyService
        
        self.gateway_factory = GatewayFactory()
        self.fraud_service = FraudService()
        self.currency_service = CurrencyService()
    
    def process_payment(self, order, payment_method, amount, currency='USD'):
        """
        Process a payment transaction.
        
        Args:
            order: Order instance
            payment_method: Payment method identifier (e.g., 'stripe', 'paystack')
            amount: Payment amount
            currency: Currency code
        
        Returns:
            dict: Payment result with status and transaction details
        
        Raises:
            PaymentError: If payment processing fails
        """
        # 1. Fraud check
        # 2. Get gateway
        # 3. Process payment
        # 4. Update order
        # 5. Return result
        pass
    
    def verify_payment(self, transaction_id):
        """
        Verify payment status with gateway.
        """
        pass
    
    def cancel_payment(self, transaction_id):
        """
        Cancel/void a pending payment.
        """
        pass
    
    def get_payment_status(self, transaction_id):
        """
        Get current payment status.
        """
        pass


class RefundService:
    """
    Handle refund operations.
    
    Refunds are a separate concern from payments.
    """
    
    def process_refund(self, payment_id, amount=None, reason=''):
        """
        Process a refund.
        
        Args:
            payment_id: Original payment ID
            amount: Refund amount (None for full refund)
            reason: Reason for refund
        """
        pass
    
    def get_refund_status(self, refund_id):
        """
        Check refund status.
        """
        pass
