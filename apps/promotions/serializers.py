from rest_framework import serializers
from .models import Coupon, FlashSale, Banner
from apps.products.serializers import ProductSerializer, CategorySerializer

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'name', 'description', 'discount_type', 'discount_value',
            'usage_limit', 'usage_limit_per_user', 'used_count', 'valid_from',
            'valid_until', 'is_active', 'minimum_order_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'used_count', 'created_at', 'updated_at']

    def validate(self, data):
        # Ensure valid_from is before valid_until
        if data['valid_from'] >= data['valid_until']:
            raise serializers.ValidationError("Valid from date must be before valid until date")
        
        # Ensure discount value is positive
        if data['discount_value'] <= 0:
            raise serializers.ValidationError("Discount value must be greater than 0")
        
        return data


class FlashSaleSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FlashSale
        fields = [
            'id', 'product', 'product_id', 'name', 'original_price', 'sale_price',
            'discount_percentage', 'start_time', 'end_time', 'is_active',
            'max_quantity', 'quantity_sold', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'discount_percentage', 'quantity_sold', 'created_at', 'updated_at']

    def validate(self, data):
        # Validate that sale price is less than original price
        if data['sale_price'] >= data['original_price']:
            raise serializers.ValidationError("Sale price must be less than original price")
        
        # Calculate discount percentage
        original = data['original_price']
        sale = data['sale_price']
        discount = ((original - sale) / original) * 100
        data['discount_percentage'] = discount
        
        # Validate time range
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("Start time must be before end time")
        
        return data


class BannerSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'subtitle', 'description', 'image', 'mobile_image',
            'background_color', 'link_url', 'position', 'order', 'is_active',
            'start_date', 'end_date', 'products', 'categories', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ApplyCouponSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(max_length=50)
    order_total = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_coupon_code(self, value):
        try:
            from .models import Coupon
            coupon = Coupon.objects.get(code=value, is_active=True)
            if not coupon.is_valid:
                raise serializers.ValidationError("Coupon is not valid")
            return coupon
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code")


class ActivePromotionsSerializer(serializers.Serializer):
    """Serializer for active promotions"""
    coupons = CouponSerializer(many=True)
    flash_sales = FlashSaleSerializer(many=True)
    banners = BannerSerializer(many=True)