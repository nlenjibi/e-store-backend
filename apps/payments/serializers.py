from rest_framework import serializers
from .models import PaymentGateway, Transaction, Refund
from apps.orders.serializers import OrderSerializer

class PaymentGatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGateway
        fields = ['id', 'name', 'display_name', 'is_active']
        read_only_fields = ['id']


class TransactionSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    order_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'order', 'order_id', 'user', 'gateway', 'transaction_type', 'status',
            'reference', 'amount', 'gateway_response', 'gateway_data', 'description',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'reference', 'created_at', 'updated_at', 'completed_at', 'user']


class RefundSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer(read_only=True)
    transaction_id = serializers.UUIDField(write_only=True)
    order = OrderSerializer(read_only=True)
    order_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Refund
        fields = [
            'id', 'transaction', 'transaction_id', 'order', 'order_id', 'user', 'reason', 'status',
            'requested_amount', 'refunded_amount', 'gateway_refund_id', 'gateway_response',
            'notes', 'requested_at', 'processed_at', 'completed_at'
        ]
        read_only_fields = ['id', 'user', 'refunded_amount', 'gateway_refund_id', 'requested_at', 'processed_at', 'completed_at']


class CreateTransactionSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    gateway_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)


class ProcessPaymentSerializer(serializers.Serializer):
    """Serializer for processing payments with gateway-specific data"""
    order_id = serializers.IntegerField()
    gateway_name = serializers.CharField(max_length=50)  # e.g., 'stripe', 'paypal', 'paystack'
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Gateway-specific fields
    card_token = serializers.CharField(required=False)  # For Stripe
    email = serializers.EmailField(required=False)  # For PayPal, Paystack
    phone = serializers.CharField(required=False)  # For mobile money
    account_number = serializers.CharField(required=False)  # For bank transfers
    
    def validate_gateway_name(self, value):
        from .models import PaymentGateway
        try:
            gateway = PaymentGateway.objects.get(name=value, is_active=True)
            return value
        except PaymentGateway.DoesNotExist:
            raise serializers.ValidationError(f"Payment gateway '{value}' is not supported or inactive")


class RefundRequestSerializer(serializers.Serializer):
    transaction_id = serializers.UUIDField()
    reason = serializers.CharField(max_length=200)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)