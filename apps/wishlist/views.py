"""Wishlist views for the e-commerce platform."""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from .models import Wishlist, WishlistActivity
from .serializers import WishlistSerializer
from apps.products.models import Product
from apps.cart.models import CartItem


class WishlistListView(generics.ListCreateAPIView):
    """List user's wishlist items and add new items."""
    
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {'success': False, 'message': 'Product already in wishlist'},
                status=status.HTTP_400_BAD_REQUEST
            )


class WishlistDetailView(generics.DestroyAPIView):
    """Remove item from wishlist."""
    
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'product_id'
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get wishlist item by product_id."""
        product_id = self.kwargs['product_id']
        return get_object_or_404(
            Wishlist,
            user=self.request.user,
            product_id=product_id
        )
    
    def perform_destroy(self, instance):
        """Log activity before deletion."""
        WishlistActivity.objects.create(
            user=instance.user,
            product=instance.product,
            action='REMOVED'
        )
        instance.delete()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wishlist_count(request):
    """Get count of items in user's wishlist."""
    count = Wishlist.objects.filter(user=request.user).count()
    return Response({'success': True, 'count': count})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_wishlist_to_cart(request):
    """Add all wishlist items to cart (only if in stock)."""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    added_count = 0
    failed_items = []
    
    for item in wishlist_items:
        if item.product.is_in_stock:
            # Add to cart
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=item.product,
                defaults={'quantity': 1}
            )
            
            if not created:
                # If already in cart, increment quantity
                cart_item.quantity += 1
                cart_item.save()
            
            # Log activity
            WishlistActivity.objects.create(
                user=request.user,
                product=item.product,
                action='MOVED_TO_CART'
            )
            
            # Remove from wishlist
            item.delete()
            added_count += 1
        else:
            failed_items.append({
                'product_id': str(item.product.id),
                'product_name': item.product.name,
                'reason': 'Out of stock'
            })
    
    return Response({
        'success': True,
        'message': f'{added_count} items added to cart',
        'added_count': added_count,
        'failed_items': failed_items
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_wishlist(request):
    """Toggle product in/out of wishlist."""
    product_id = request.data.get('product_id')
    
    if not product_id:
        return Response(
            {'success': False, 'message': 'product_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        product = Product.objects.get(id=product_id, is_active=True, is_deleted=False)
    except Product.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if already in wishlist
    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    ).first()
    
    if wishlist_item:
        # Remove from wishlist
        WishlistActivity.objects.create(
            user=request.user,
            product=product,
            action='REMOVED'
        )
        wishlist_item.delete()
        return Response({
            'success': True,
            'message': 'Product removed from wishlist',
            'in_wishlist': False
        })
    else:
        # Add to wishlist
        wishlist_item = Wishlist.objects.create(
            user=request.user,
            product=product
        )
        WishlistActivity.objects.create(
            user=request.user,
            product=product,
            action='ADDED'
        )
        return Response({
            'success': True,
            'message': 'Product added to wishlist',
            'in_wishlist': True,
            'wishlist_item': WishlistSerializer(wishlist_item).data
        }, status=status.HTTP_201_CREATED)

