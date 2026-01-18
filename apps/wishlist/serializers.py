"""Wishlist serializers."""
from rest_framework import serializers
from .models import Wishlist, WishlistActivity
from apps.products.serializers import ProductListSerializer


class WishlistSerializer(serializers.ModelSerializer):
    """Wishlist serializer with product details."""
    
    product = ProductListSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    is_in_stock = serializers.ReadOnlyField()
    can_add_to_cart = serializers.ReadOnlyField()
    
    class Meta:
        model = Wishlist
        fields = [
            'id', 'user', 'product', 'product_id', 'added_at', 
            'is_in_stock', 'can_add_to_cart'
        ]
        read_only_fields = ['id', 'user', 'added_at']
    
    def create(self, validated_data):
        """Create wishlist item."""
        from apps.products.models import Product
        
        product_id = validated_data.pop('product_id')
        product = Product.objects.get(id=product_id)
        
        wishlist_item = Wishlist.objects.create(
            product=product,
            **validated_data
        )
        
        # Log activity
        WishlistActivity.objects.create(
            user=wishlist_item.user,
            product=product,
            action='ADDED'
        )
        
        return wishlist_item


class WishlistActivitySerializer(serializers.ModelSerializer):
    """Wishlist activity serializer."""
    
    class Meta:
        model = WishlistActivity
        fields = ['id', 'user', 'product', 'action', 'timestamp']
        read_only_fields = ['id', 'timestamp']
