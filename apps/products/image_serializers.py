"""Product Image serializers."""
from rest_framework import serializers
from apps.products.models import ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images."""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image_url', 'alt_text', 'is_primary', 'display_order', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        """Validate image data."""
        # Ensure display_order is positive
        if 'display_order' in data and data['display_order'] < 0:
            raise serializers.ValidationError({'display_order': 'Display order must be non-negative'})
        
        return data
    
    def create(self, validated_data):
        """Create product image and handle primary image logic."""
        product = validated_data.get('product')
        is_primary = validated_data.get('is_primary', False)
        
        # If this is the first image for the product, make it primary
        if not ProductImage.objects.filter(product=product).exists():
            validated_data['is_primary'] = True
        
        return super().create(validated_data)


class ProductImageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating product images (without product field)."""
    
    class Meta:
        model = ProductImage
        fields = ['image_url', 'alt_text', 'is_primary', 'display_order']
    
    def validate_image_url(self, value):
        """Validate that the image URL is valid."""
        if not value:
            raise serializers.ValidationError('Image URL is required')
        
        # Basic URL validation
        if not value.startswith('http://') and not value.startswith('https://'):
            raise serializers.ValidationError('Image URL must start with http:// or https://')
        
        return value


class ProductImageUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating product images."""
    
    class Meta:
        model = ProductImage
        fields = ['image_url', 'alt_text', 'is_primary', 'display_order']
    
    def validate_image_url(self, value):
        """Validate that the image URL is valid."""
        if value and not value.startswith('http://') and not value.startswith('https://'):
            raise serializers.ValidationError('Image URL must start with http:// or https://')
        
        return value
