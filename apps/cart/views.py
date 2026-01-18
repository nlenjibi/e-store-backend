from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer, UpdateCartItemSerializer
from apps.products.models import Product


def get_or_create_user_cart(user):
    """Get or create a cart for authenticated user"""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


def get_or_create_guest_cart(session_key):
    """Get or create a cart for guest user"""
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    """Get authenticated user's cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """Add item to authenticated user's cart"""
    serializer = AddToCartSerializer(data=request.data)
    if serializer.is_valid():
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if product.stock < quantity:
            return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        # Update product stock
        product.stock -= quantity
        product.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    serializer = UpdateCartItemSerializer(data=request.data)
    if serializer.is_valid():
        new_quantity = serializer.validated_data['quantity']
        
        # Check if there's enough stock
        if cart_item.product.stock + cart_item.quantity < new_quantity:
            return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Adjust product stock
        stock_difference = new_quantity - cart_item.quantity
        cart_item.product.stock -= stock_difference
        cart_item.product.save()
        
        cart_item.quantity = new_quantity
        cart_item.save()
        
        cart = cart_item.cart
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    # Return stock to product
    cart_item.product.stock += cart_item.quantity
    cart_item.product.save()
    
    cart_item.delete()
    
    cart = get_or_create_user_cart(request.user)
    cart_serializer = CartSerializer(cart)
    return Response(cart_serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """Clear all items from cart"""
    cart = get_object_or_404(Cart, user=request.user)
    
    # Return all stock to products
    for item in cart.items.all():
        item.product.stock += item.quantity
        item.product.save()
    
    cart.items.all().delete()
    
    cart_serializer = CartSerializer(cart)
    return Response(cart_serializer.data)


@api_view(['POST'])
def guest_add_to_cart(request):
    """Add item to guest cart using session"""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    serializer = AddToCartSerializer(data=request.data)
    if serializer.is_valid():
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if product.stock < quantity:
            return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart = get_or_create_guest_cart(session_key)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        # Update product stock
        product.stock -= quantity
        product.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def guest_get_cart(request):
    """Get guest cart using session"""
    session_key = request.session.session_key
    if not session_key:
        # Return empty cart if no session
        return Response({
            'id': None,
            'user': None,
            'session_key': None,
            'items': [],
            'total_cost': 0,
            'total_items': 0
        })
    
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    serializer = CartSerializer(cart)
    return Response(serializer.data)