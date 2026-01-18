"""
Currency Service
----------------
Handles currency conversion and validation.

Responsibilities:
✓ Convert between currencies
✓ Get current exchange rates
✓ Validate currency codes
✓ Format amounts for display
✓ Handle multi-currency payments

For production, integrate with:
- OpenExchangeRates API
- XE.com API
- ECB (European Central Bank)
"""
from decimal import Decimal


class CurrencyService:
    """
    Currency management and conversion.
    
    Simple implementation with fallback to static rates.
    For production, use a real exchange rate API.
    """
    
    # Supported currencies
    SUPPORTED_CURRENCIES = [
        'USD', 'EUR', 'GBP', 'NGN', 'GHS', 'KES', 'UGX', 'ZAR'
    ]
    
    # Fallback rates (relative to USD)
    # Update these regularly or fetch from API
    STATIC_RATES = {
        'USD': 1.0,
        'EUR': 0.85,
        'GBP': 0.73,
        'NGN': 1600.0,   # Nigerian Naira
        'GHS': 16.0,     # Ghanaian Cedi
        'KES': 160.0,    # Kenyan Shilling
        'UGX': 3700.0,   # Ugandan Shilling
        'ZAR': 18.5,     # South African Rand
    }
    
    def convert(self, amount, from_currency, to_currency):
        """
        Convert amount between currencies.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
        
        Returns:
            Decimal: Converted amount
        """
        if from_currency == to_currency:
            return Decimal(amount)
        
        # Convert to USD first, then to target
        usd_amount = Decimal(amount) / Decimal(self.STATIC_RATES[from_currency])
        target_amount = usd_amount * Decimal(self.STATIC_RATES[to_currency])
        
        return target_amount.quantize(Decimal('0.01'))
    
    def get_exchange_rate(self, from_currency, to_currency):
        """
        Get current exchange rate.
        """
        if from_currency == to_currency:
            return Decimal('1.0')
        
        rate = (Decimal(self.STATIC_RATES[to_currency]) / 
                Decimal(self.STATIC_RATES[from_currency]))
        
        return rate
    
    def validate_currency(self, currency_code):
        """
        Check if currency is supported.
        """
        return currency_code in self.SUPPORTED_CURRENCIES
    
    def format_amount(self, amount, currency):
        """
        Format amount for display with currency symbol.
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
        return f"{symbol}{amount:,.2f}"
