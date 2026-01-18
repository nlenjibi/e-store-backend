from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer, OrderUpdateSerializer
from apps.cart.models import Cart


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_orders(request):
    """Get all orders for the authenticated user"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request, order_id):
    """Get a specific order for the authenticated user"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Create a new order from cart or provided items"""
    serializer = OrderCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Check if user wants to create order from cart
        from_cart = request.data.get('from_cart', False)
        
        if from_cart:
            # Get user's cart
            try:
                cart = Cart.objects.get(user=request.user)
                if not cart.items.exists():
                    return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Prepare order data from cart
                order_data = {
                    'user': request.user,
                    'items': []
                }
                
                # Copy shipping and billing data from request
                for field in ['shipping_address', 'shipping_city', 'shipping_state', 'shipping_country', 'shipping_postal_code',
                              'billing_address', 'billing_city', 'billing_state', 'billing_country', 'billing_postal_code', 'notes']:
                    if field in request.data:
                        order_data[field] = request.data[field]
                
                # Create order items from cart items
                for cart_item in cart.items.all():
                    order_data['items'].append({
                        'product': cart_item.product,
                        'quantity': cart_item.quantity,
                        'price': cart_item.product.final_price
                    })
                
                # Create the order
                order = Order.objects.create(**{k: v for k, v in order_data.items() if k != 'items'})
                
                # Create order items and update stock
                subtotal = 0
                for item_data in order_data['items']:
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=item_data['product'],
                        quantity=item_data['quantity'],
                        price=item_data['price']
                    )
                    subtotal += order_item.total_price
                    
                    # Reduce product stock
                    product = item_data['product']
                    product.stock -= item_data['quantity']
                    product.save()
                
                # Calculate totals
                order.subtotal = subtotal
                order.total_amount = subtotal + order.shipping_cost - order.discount_amount
                order.save()
                
                # Clear the cart after successful order creation
                cart.items.all().delete()
                
                order_serializer = OrderSerializer(order)
                return Response(order_serializer.data, status=status.HTTP_201_CREATED)
                
            except Cart.DoesNotExist:
                return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            # Create order from provided data
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_order(request, order_id):
    """Update order status (for users or admins)"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Only allow status updates for non-admin users
    allowed_fields = ['status', 'payment_status', 'notes']
    update_data = {k: v for k, v in request.data.items() if k in allowed_fields}
    
    serializer = OrderUpdateSerializer(order, data=update_data, partial=request.method == 'PATCH')
    if serializer.is_valid():
        serializer.save()
        return Response(OrderSerializer(order).data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_stats(request):
    """Get order statistics for the authenticated user"""
    orders = Order.objects.filter(user=request.user)
    
    stats = {
        'total_orders': orders.count(),
        'total_spent': sum(order.total_amount for order in orders if order.payment_status == 'paid'),
        'pending_orders': orders.filter(status='pending').count(),
        'completed_orders': orders.filter(status='delivered').count(),
        'cancelled_orders': orders.filter(status='cancelled').count(),
    }
    
    return Response(stats)