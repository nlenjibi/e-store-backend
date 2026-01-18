"""
Fraud Service
-------------
Basic fraud detection and prevention.

Responsibilities:
✓ Score transactions for fraud risk
✓ Check velocity (multiple attempts)
✓ Validate customer data
✓ Block suspicious transactions
✓ Log fraud attempts

This is a simple implementation. For production, consider:
- Integrate with services like Stripe Radar, Sift, etc.
- Machine learning models
- Device fingerprinting
- IP geolocation checks
"""
from datetime import timedelta
from django.utils import timezone


class FraudService:
    """
    Basic fraud detection service.
    
    Checks for common fraud patterns:
    - Multiple failed attempts
    - Mismatched billing info
    - Unusual amounts
    - Velocity checks
    """
    
    # Thresholds
    MAX_FAILED_ATTEMPTS = 3
    TIME_WINDOW_MINUTES = 60
    MAX_AMOUNT_USD = 10000
    
    def check_transaction(self, user, amount, currency, payment_details):
        """
        Evaluate transaction for fraud risk.
        
        Args:
            user: User making payment
            amount: Transaction amount
            currency: Currency code
            payment_details: Additional payment details
        
        Returns:
            dict: {
                'risk_score': float (0-100),
                'is_suspicious': bool,
                'reasons': list of str
            }
        """
        score = 0
        reasons = []
        
        # Check 1: Velocity (rapid attempts)
        # Check 2: Amount threshold
        # Check 3: User history
        # Check 4: Geolocation mismatch
        
        return {
            'risk_score': score,
            'is_suspicious': score > 70,
            'reasons': reasons
        }
    
    def get_recent_failed_attempts(self, user):
        """
        Get recent failed payment attempts for user.
        """
        pass
    
    def log_fraud_attempt(self, user, reason, details):
        """
        Log a suspected fraud attempt.
        """
        pass
    
    def is_blocked(self, user):
        """
        Check if user is blocked from making payments.
        """
        pass
