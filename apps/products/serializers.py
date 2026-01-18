"""Serializers for the products app."""
from rest_framework import serializers
from .models import Category, Brand, Product, ProductImage, ProductReview, ProductView, ProductSearch


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category model."""
    
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at', 'is_deleted')
        lookup_field = 'slug'


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for brand model."""
    
    class Meta:
        model = Brand
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product image model (URL-based)."""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'alt_text', 'is_primary', 'display_order', 'created_at']
        read_only_fields = ('id', 'created_at')


class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer for product review model."""
    
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ProductReview
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'helpful_count')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product model with multiple image URL support."""
    
    category = CategorySerializer(read_only=True)
    category_slug = serializers.SlugRelatedField(
        queryset=Category.objects.filter(is_active=True, is_deleted=False),
        slug_field='slug',
        source='category',
        write_only=True,
        required=False
    )
    brand = BrandSerializer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.filter(is_active=True),
        source='brand',
        write_only=True,
        required=False
    )
    images = serializers.ListField(
        child=serializers.URLField(max_length=500),
        required=False,
        help_text='List of image URLs'
    )
    primary_image = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    final_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    reviews = ProductReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description', 'sku', 'barcode',
            'category', 'category_slug', 'brand', 'brand_id', 'images', 'primary_image',
            'price', 'discount_price', 'discount_percent', 'final_price', 'discount_percentage',
            'tax_rate', 'stock_quantity', 'stock_status', 'min_stock_level', 'shipping_type',
            'is_active', 'is_featured', 'is_trending', 'is_new', 'weight', 'dimensions',
            'color', 'size', 'material', 'warranty_period', 'shipping_cost', 'rating',
            'num_reviews', 'reviews', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at', 'num_reviews', 
                           'rating', 'is_deleted', 'final_price', 'discount_percentage')
        lookup_field = 'slug'
    
    def get_primary_image(self, obj):
        """Get the first image URL as primary."""
        if obj.images and len(obj.images) > 0:
            return obj.images[0]
        return None
    
    def get_stock_status(self, obj):
        """Get stock status as string."""
        return "IN_STOCK" if obj.stock_quantity > 0 else "OUT_OF_STOCK"
    
    def validate_images(self, value):
        """Validate image URLs."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Images must be a list of URLs.")
        if len(value) > 10:
            raise serializers.ValidationError("Maximum of 10 images allowed per product.")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list view (lighter version)."""
    
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    final_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'price', 'discount_price', 'final_price',
            'discount_percentage', 'stock_quantity', 'stock_status', 'shipping_type',
            'is_active', 'is_featured', 'is_trending', 'rating', 'num_reviews', 
            'category', 'brand', 'primary_image', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at', 'stock_status', 
                           'final_price', 'discount_percentage')
        lookup_field = 'slug'
    
    def get_primary_image(self, obj):
        """Get the first image URL as primary."""
        if obj.images and len(obj.images) > 0:
            return obj.images[0]
        return None
    
    def get_stock_status(self, obj):
        """Get stock status as string."""
        return "IN_STOCK" if obj.stock_quantity > 0 else "OUT_OF_STOCK"


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin product creation and updates."""
    
    category_slug = serializers.SlugRelatedField(
        queryset=Category.objects.filter(is_active=True, is_deleted=False),
        slug_field='slug',
        source='category',
        required=True
    )
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.filter(is_active=True),
        source='brand',
        required=False,
        allow_null=True
    )
    images = serializers.ListField(
        child=serializers.URLField(max_length=500),
        required=False,
        allow_empty=True,
        help_text='List of image URLs'
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'short_description', 'sku', 'barcode',
            'category_slug', 'brand_id', 'images', 'price', 'discount_price',
            'discount_percent', 'tax_rate', 'stock_quantity', 'min_stock_level',
            'shipping_type', 'is_active', 'is_featured', 'is_trending', 'is_new',
            'weight', 'dimensions', 'color', 'size', 'material', 'warranty_period',
            'shipping_cost'
        ]
    
    def validate_images(self, value):
        """Validate image URLs."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Images must be a list of URLs.")
        if len(value) > 10:
            raise serializers.ValidationError("Maximum of 10 images allowed per product.")
        return value
    
    def validate(self, data):
        """Validate discount price and stock quantity."""
        if 'price' in data and 'discount_price' in data:
            if data.get('discount_price') and data['discount_price'] >= data['price']:
                raise serializers.ValidationError({
                    'discount_price': 'Discount price must be less than regular price.'
                })
        
        if 'stock_quantity' in data and data['stock_quantity'] < 0:
            raise serializers.ValidationError({
                'stock_quantity': 'Stock quantity cannot be negative.'
            })
        
        return data


class ProductImageManagementSerializer(serializers.Serializer):
    """Serializer for managing individual product images."""
    
    image_url = serializers.URLField(max_length=500, required=True)
    
    def validate_image_url(self, value):
        """Validate image URL."""
        if not value:
            raise serializers.ValidationError("Image URL is required.")
        return value


class ProductSearchSerializer(serializers.ModelSerializer):
    """Serializer for product search model."""
    
    class Meta:
        model = ProductSearch
        fields = '__all__'
        read_only_fields = ('id', 'user', 'session_key', 'ip_address', 'timestamp')