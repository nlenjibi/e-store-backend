"""
Core Utilities
--------------
Reusable utility functions for the entire project.

Purpose:
- DRY principle
- Common operations
- Helper functions
"""
import random
import string
from datetime import datetime, timedelta
from django.utils import timezone


def generate_random_string(length=10, include_digits=True, include_special=False):
    """
    Generate a random string.
    
    Args:
        length: Length of string
        include_digits: Include numbers
        include_special: Include special characters
    
    Returns:
        str: Random string
    """
    chars = string.ascii_letters
    
    if include_digits:
        chars += string.digits
    
    if include_special:
        chars += string.punctuation
    
    return ''.join(random.choice(chars) for _ in range(length))


def generate_order_number():
    """
    Generate unique order number.
    
    Format: ORD-YYYYMMDD-XXXXX
    Example: ORD-20260104-A3F9K
    """
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = generate_random_string(5, include_digits=True, include_special=False).upper()
    
    return f"ORD-{date_part}-{random_part}"


def generate_transaction_reference():
    """
    Generate unique transaction reference.
    
    Format: TXN-TIMESTAMP-XXXXX
    """
    timestamp = int(datetime.now().timestamp())
    random_part = generate_random_string(5, include_digits=True).upper()
    
    return f"TXN-{timestamp}-{random_part}"


def format_currency(amount, currency='USD'):
    """
    Format amount with currency symbol.
    
    Args:
        amount: Numeric amount
        currency: Currency code
    
    Returns:
        str: Formatted string
    """
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'NGN': '₦',
        'GHS': 'GH₵',
        'KES': 'KSh',
        'UGX': 'USh',
        'ZAR': 'R',
    }
    
    symbol = symbols.get(currency, currency)
    
    try:
        return f"{symbol}{float(amount):,.2f}"
    except (ValueError, TypeError):
        return f"{symbol}0.00"


def calculate_percentage(part, whole):
    """
    Calculate percentage.
    
    Args:
        part: Part value
        whole: Whole value
    
    Returns:
        float: Percentage
    """
    if whole == 0:
        return 0.0
    
    return round((part / whole) * 100, 2)


def truncate_string(text, length=100, suffix='...'):
    """
    Truncate string to specified length.
    """
    if len(text) <= length:
        return text
    
    return text[:length].rsplit(' ', 1)[0] + suffix


def get_client_ip(request):
    """
    Get client IP address from request.
    
    Handles proxy headers.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip


def is_expired(expiry_date):
    """
    Check if a date has expired.
    
    Args:
        expiry_date: datetime object
    
    Returns:
        bool: True if expired
    """
    if not expiry_date:
        return False
    
    return timezone.now() > expiry_date


def add_days_to_date(date, days):
    """
    Add days to a date.
    """
    return date + timedelta(days=days)


def get_date_range(days_back=30):
    """
    Get date range for analytics.
    
    Args:
        days_back: Number of days to go back
    
    Returns:
        tuple: (start_date, end_date)
    """
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days_back)
    
    return start_date, end_date
