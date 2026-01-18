"""
Payment Validators
------------------
Input validation for payment operations.

Responsibilities:
- Validate payment amounts
- Validate currency codes
- Validate payment methods
- Validate customer data
"""
from decimal import Decimal
from django.core.exceptions import ValidationError


def validate_amount(amount):
    """
    Validate payment amount.
    
    Args:
        amount: Payment amount to validate
    
    Raises:
        ValidationError: If amount is invalid
    """
    try:
        amount = Decimal(str(amount))
    except:
        raise ValidationError("Invalid amount format")
    
    if amount <= 0:
        raise ValidationError("Amount must be greater than zero")
    
    if amount > Decimal('1000000'):  # 1 million limit
        raise ValidationError("Amount exceeds maximum allowed")
    
    return amount


def validate_currency(currency_code):
    """
    Validate currency code.
    """
    from .services.currency_service import CurrencyService
    
    service = CurrencyService()
    
    if not service.validate_currency(currency_code):
        raise ValidationError(f"Unsupported currency: {currency_code}")
    
    return currency_code.upper()


def validate_payment_method(method):
    """
    Validate payment method.
    """
    valid_methods = ['stripe', 'paystack', 'flutterwave', 'mtn_momo']
    
    if method not in valid_methods:
        raise ValidationError(f"Invalid payment method: {method}")
    
    return method
