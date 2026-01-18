"""
Payment Gateways Package
------------------------
This package contains all payment gateway integrations.

Each gateway implements the BaseGateway interface,
ensuring consistent behavior across all payment providers.

Architecture:
- Base gateway defines the contract (interface)
- Each gateway implements specific provider logic
- Gateways are instantiated by GatewayFactory
- Services interact only with the base interface

Gateways included:
- Stripe: Global payments (cards, digital wallets)
- Paystack: African markets (Nigeria, Ghana, South Africa)
- Flutterwave: Pan-African payments
- MTN MoMo: Mobile money (Uganda, other African markets)

Adding new gateways:
1. Create new file: {provider}_gateway.py
2. Inherit from BaseGateway
3. Implement all required methods
4. Register in GatewayFactory
"""
