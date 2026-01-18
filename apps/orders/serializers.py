from rest_framework import serializers
from .models import Order, OrderItem
from apps.products.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status', 'items', 'total_items',
            'shipping_address', 'shipping_city', 'shipping_state', 'shipping_country', 'shipping_postal_code',
            'billing_address', 'billing_city', 'billing_state', 'billing_country', 'billing_postal_code',
            'subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount',
            'notes', 'created_at', 'updated_at', 'estimated_delivery'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at', 'total_items']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'items', 'shipping_address', 'shipping_city', 'shipping_state', 'shipping_country', 'shipping_postal_code',
            'billing_address', 'billing_city', 'billing_state', 'billing_country', 'billing_postal_code',
            'notes'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        # Calculate totals
        subtotal = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = item_data.get('price', product.final_price)
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
            
            subtotal += price * quantity
        
        # Calculate totals
        order.subtotal = subtotal
        order.total_amount = subtotal + order.shipping_cost - order.discount_amount
        order.save()
        
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'payment_status', 'notes']

    def update(self, instance, validated_data):
        # Only allow certain status changes
        if 'status' in validated_data:
            old_status = instance.status
            new_status = validated_data['status']
            
            # Define valid status transitions
            valid_transitions = {
                'pending': ['confirmed', 'cancelled'],
                'confirmed': ['processing', 'cancelled'],
                'processing': ['shipped'],
                'shipped': ['delivered'],
                'delivered': [],
                'cancelled': [],
                'refunded': []
            }
            
            if new_status not in valid_transitions.get(old_status, []):
                raise serializers.ValidationError(f"Cannot change status from {old_status} to {new_status}")
        
        return super().update(instance, validated_data)