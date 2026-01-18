from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import F
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.conf import settings
from .models import Coupon, FlashSale, Banner
from .serializers import (
    CouponSerializer, FlashSaleSerializer, BannerSerializer, 
    ApplyCouponSerializer, ActivePromotionsSerializer
)
from apps.products.models import Product


@api_view(['GET'])
@cache_page(60 * 5)  # Cache for 5 minutes
def list_active_coupons(request):
    """Get all active coupons"""
    now = timezone.now()
    coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=now,
        valid_until__gte=now
    )
    serializer = CouponSerializer(coupons, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@cache_page(60 * 5)  # Cache for 5 minutes
def list_active_flash_sales(request):
    """Get all active flash sales"""
    now = timezone.now()
    flash_sales = FlashSale.objects.filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now,
        quantity_sold__lt=F('max_quantity')  # Not sold out
    ).select_related('product')
    serializer = FlashSaleSerializer(flash_sales, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@cache_page(60 * 5)  # Cache for 5 minutes
def list_active_banners(request):
    """Get all active banners"""
    now = timezone.now()
    banners = Banner.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).prefetch_related('products', 'categories')
    serializer = BannerSerializer(banners, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@cache_page(60 * 5)  # Cache for 5 minutes
def get_active_promotions(request):
    """Get all active promotions (coupons, flash sales, banners)"""
    now = timezone.now()
    
    # Get active coupons
    coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=now,
        valid_until__gte=now
    )
    
    # Get active flash sales
    flash_sales = FlashSale.objects.filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now,
        quantity_sold__lt=F('max_quantity')
    ).select_related('product')
    
    # Get active banners
    banners = Banner.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).prefetch_related('products', 'categories')
    
    # Serialize all data
    coupon_serializer = CouponSerializer(coupons, many=True)
    flash_sale_serializer = FlashSaleSerializer(flash_sales, many=True)
    banner_serializer = BannerSerializer(banners, many=True)
    
    data = {
        'coupons': coupon_serializer.data,
        'flash_sales': flash_sale_serializer.data,
        'banners': banner_serializer.data
    }
    
    serializer = ActivePromotionsSerializer(data)
    return Response(data)


@api_view(['POST'])
def apply_coupon(request):
    """Apply a coupon to an order total"""
    serializer = ApplyCouponSerializer(data=request.data)
    if serializer.is_valid():
        coupon = serializer.validated_data['coupon']
        order_total = serializer.validated_data['order_total']
        
        # Check if coupon is valid for this user and order
        if not coupon.is_valid_for_user(request.user):
            return Response({
                'valid': False,
                'error': 'Coupon is not valid for you'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if order_total < coupon.minimum_order_amount:
            return Response({
                'valid': False,
                'error': f'Minimum order amount of {coupon.minimum_order_amount} not met'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if coupon applies to specific products/categories
        if coupon.products.exists() or coupon.categories.exists():
            # In a real app, we'd validate against cart items
            pass  # Simplified for now
        
        # Calculate discount
        discount_amount = coupon.calculate_discount(order_total)
        
        return Response({
            'valid': True,
            'coupon': CouponSerializer(coupon).data,
            'discount_amount': float(discount_amount),
            'new_total': float(order_total - discount_amount)
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_product_flash_sales(request, product_id):
    """Get flash sales for a specific product"""
    product = get_object_or_404(Product, id=product_id)
    now = timezone.now()
    flash_sales = FlashSale.objects.filter(
        product=product,
        is_active=True,
        start_time__lte=now,
        end_time__gte=now,
        quantity_sold__lt=models.F('max_quantity')
    )
    serializer = FlashSaleSerializer(flash_sales, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_list_coupons(request):
    """Admin: List all coupons (including inactive)"""
    coupons = Coupon.objects.all()
    serializer = CouponSerializer(coupons, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_create_coupon(request):
    """Admin: Create a new coupon"""
    serializer = CouponSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_list_flash_sales(request):
    """Admin: List all flash sales"""
    flash_sales = FlashSale.objects.all().select_related('product')
    serializer = FlashSaleSerializer(flash_sales, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_create_flash_sale(request):
    """Admin: Create a new flash sale"""
    serializer = FlashSaleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_list_banners(request):
    """Admin: List all banners"""
    banners = Banner.objects.all().prefetch_related('products', 'categories')
    serializer = BannerSerializer(banners, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_create_banner(request):
    """Admin: Create a new banner"""
    serializer = BannerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)