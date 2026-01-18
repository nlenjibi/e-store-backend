"""
Gateway Factory
---------------
Responsible for selecting and instantiating the correct payment gateway.

This implements the Factory Pattern.

Responsibilities:
✓ Select gateway based on criteria (currency, region, etc.)
✓ Instantiate gateway with proper configuration
✓ Handle gateway unavailability
✓ Provide gateway fallback logic

Why a factory?
- Centralizes gateway selection logic
- Makes adding new gateways easy
- Enables A/B testing of gateways
- Supports regional gateway routing
"""


class GatewayFactory:
    """
    Factory for creating payment gateway instances.
    
    Usage:
        factory = GatewayFactory()
        gateway = factory.get_gateway('stripe')
        # or
        gateway = factory.get_gateway_for_region('NGN', 'NG')
    """
    
    # Gateway registry
    GATEWAYS = {
        'stripe': 'apps.payments.gateways.stripe_gateway.StripeGateway',
        'paystack': 'apps.payments.gateways.paystack_gateway.PaystackGateway',
        'flutterwave': 'apps.payments.gateways.flutterwave_gateway.FlutterwaveGateway',
        'mtn_momo': 'apps.payments.gateways.mtn_momo_gateway.MTNMoMoGateway',
    }
    
    # Regional preferences
    REGIONAL_PREFERENCES = {
        'NG': ['paystack', 'flutterwave'],  # Nigeria
        'GH': ['paystack', 'flutterwave'],  # Ghana
        'KE': ['flutterwave'],              # Kenya
        'UG': ['flutterwave', 'mtn_momo'],  # Uganda
        'US': ['stripe'],                    # United States
        'EU': ['stripe'],                    # Europe
    }
    
    def get_gateway(self, gateway_name):
        """
        Get a specific gateway by name.
        
        Args:
            gateway_name: Gateway identifier (e.g., 'stripe')
        
        Returns:
            Gateway instance
        
        Raises:
            ValueError: If gateway not found
        """
        pass
    
    def get_gateway_for_region(self, currency, country_code):
        """
        Get the best gateway for a region/currency.
        
        This enables smart routing:
        - Nigerian customers → Paystack/Flutterwave
        - US/EU customers → Stripe
        - East Africa → Flutterwave/MTN MoMo
        
        Args:
            currency: Currency code (e.g., 'NGN', 'USD')
            country_code: ISO country code
        
        Returns:
            Gateway instance
        """
        pass
    
    def get_available_gateways(self):
        """
        Get list of all available configured gateways.
        """
        pass
    
    def _instantiate_gateway(self, gateway_class_path):
        """
        Dynamically import and instantiate a gateway.
        """
        pass
