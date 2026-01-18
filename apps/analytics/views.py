from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta
from decimal import Decimal
from core.cache_utils import CacheManager, CacheKeyBuilder
from .models import RevenueSnapshot, ProductView, UserSearch, CartAbandonment, UserBehavior
from apps.auth.models import User
from apps.products.models import Product
from apps.orders.models import Order
from .serializers import (
    RevenueSnapshotSerializer, ProductViewSerializer, UserSearchSerializer,
    CartAbandonmentSerializer, UserBehaviorSerializer,
    RevenueAnalyticsSerializer, UserAnalyticsSerializer, ProductAnalyticsSerializer
)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_revenue_analytics(request):
    """Get comprehensive revenue analytics"""
    # Date range from query params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Default to last 30 days if no dates provided
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Build cache key including date range
    cache_key = CacheKeyBuilder.build(
        'analytics',
        'revenue',
        start_date=str(start_date),
        end_date=str(end_date)
    )
    
    # Try to get from cache
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)
    
    # Get revenue snapshots for the date range
    snapshots = RevenueSnapshot.objects.filter(
        date__range=[start_date, end_date]
    ).order_by('date')
    
    # Calculate overall metrics
    total_revenue = sum(snapshot.total_revenue for snapshot in snapshots)
    total_orders = sum(snapshot.total_orders for snapshot in snapshots)
    total_customers = sum(snapshot.total_customers for snapshot in snapshots)
    
    avg_order_value = total_revenue / total_orders if total_orders > 0 else Decimal('0.00')
    
    # Payment method breakdown
    cash_on_delivery = sum(snapshot.cash_on_delivery for snapshot in snapshots)
    card_payments = sum(snapshot.card_payments for snapshot in snapshots)
    mobile_money = sum(snapshot.mobile_money for snapshot in snapshots)
    other_payments = sum(snapshot.other_payments for snapshot in snapshots)
    
    revenue_by_payment_method = {
        'cash_on_delivery': cash_on_delivery,
        'card_payments': card_payments,
        'mobile_money': mobile_money,
        'other_payments': other_payments,
    }
    
    # Revenue trend (daily)
    revenue_trend = []
    for snapshot in snapshots:
        revenue_trend.append({
            'date': snapshot.date.isoformat(),
            'revenue': float(snapshot.total_revenue),
            'orders': snapshot.total_orders
        })
    
    data = {
        'total_revenue': float(total_revenue),
        'total_orders': total_orders,
        'total_customers': total_customers,
        'avg_order_value': float(avg_order_value),
        'revenue_by_payment_method': revenue_by_payment_method,
        'revenue_trend': revenue_trend
    }
    
    # Cache for 10 minutes
    cache.set(cache_key, data, settings.CACHE_TTL['SHORT'])
    
    serializer = RevenueAnalyticsSerializer(data)
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_user_analytics(request):
    """Get user analytics"""
    # Date range from query params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Calculate user metrics
    total_users = User.objects.count()
    active_users = User.objects.filter(
        last_login__date__range=[start_date, end_date]
    ).count()
    
    new_users_today = User.objects.filter(
        date_joined__date=timezone.now().date()
    ).count()
    
    # Calculate user growth rate (simplified)
    total_users_prev_period = User.objects.filter(
        date_joined__date__lt=start_date
    ).count()
    
    if total_users_prev_period > 0:
        user_growth_rate = ((total_users - total_users_prev_period) / total_users_prev_period) * 100
    else:
        user_growth_rate = Decimal('100.00')  # First users
    
    data = {
        'total_users': total_users,
        'active_users': active_users,
        'new_users_today': new_users_today,
        'user_growth_rate': float(user_growth_rate)
    }
    
    serializer = UserAnalyticsSerializer(data)
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_product_analytics(request):
    """Get product analytics"""
    # Date range from query params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Top selling products
    top_selling_products = Order.objects.filter(
        created_at__date__range=[start_date, end_date],
        payment_status='paid'
    ).values(
        'items__product__id', 'items__product__name', 'items__product__price'
    ).annotate(
        total_sold=Sum('items__quantity')
    ).order_by('-total_sold')[:10]
    
    # Most viewed products
    most_viewed_products = ProductView.objects.filter(
        viewed_at__date__range=[start_date, end_date]
    ).values(
        'product__id', 'product__name'
    ).annotate(
        view_count=Count('id')
    ).order_by('-view_count')[:10]
    
    # Conversion rates (simplified calculation)
    total_product_views = ProductView.objects.filter(
        viewed_at__date__range=[start_date, end_date]
    ).count()
    
    total_purchases = Order.objects.filter(
        created_at__date__range=[start_date, end_date],
        payment_status='paid'
    ).count()
    
    conversion_rate = (total_purchases / total_product_views * 100) if total_product_views > 0 else 0
    
    data = {
        'top_selling_products': list(top_selling_products),
        'most_viewed_products': list(most_viewed_products),
        'conversion_rates': {
            'overall_conversion_rate': float(conversion_rate)
        }
    }
    
    serializer = ProductAnalyticsSerializer(data)
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_order_analytics(request):
    """Get order analytics"""
    # Date range from query params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Order status breakdown
    orders_by_status = Order.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).values('status').annotate(count=Count('id'))
    
    # Payment status breakdown
    orders_by_payment_status = Order.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).values('payment_status').annotate(count=Count('id'))
    
    # Average order value
    avg_order_value = Order.objects.filter(
        created_at__date__range=[start_date, end_date],
        payment_status='paid'
    ).aggregate(avg=Avg('total_amount'))['avg'] or Decimal('0.00')
    
    # Orders by day
    orders_by_day = Order.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).extra({'date': "date(created_at)"}).values('date').annotate(
        count=Count('id'),
        total_revenue=Sum('total_amount')
    ).order_by('date')
    
    data = {
        'orders_by_status': list(orders_by_status),
        'orders_by_payment_status': list(orders_by_payment_status),
        'avg_order_value': float(avg_order_value),
        'orders_by_day': list(orders_by_day)
    }
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_behavior_analytics(request):
    """Get user behavior analytics"""
    # Date range from query params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Behavior breakdown by action
    behavior_by_action = UserBehavior.objects.filter(
        timestamp__date__range=[start_date, end_date]
    ).values('action').annotate(count=Count('id')).order_by('-count')
    
    # Top search queries
    top_searches = UserSearch.objects.filter(
        searched_at__date__range=[start_date, end_date]
    ).values('query').annotate(count=Count('id')).order_by('-count')[:10]
    
    # Cart abandonment rate
    total_carts = UserBehavior.objects.filter(
        timestamp__date__range=[start_date, end_date],
        action='checkout_start'
    ).count()
    
    recovered_carts = CartAbandonment.objects.filter(
        abandoned_at__date__range=[start_date, end_date],
        recovered=True
    ).count()
    
    cart_abandonment_rate = 0
    if total_carts > 0:
        abandoned_carts = CartAbandonment.objects.filter(
            abandoned_at__date__range=[start_date, end_date]
        ).count()
        cart_abandonment_rate = (abandoned_carts / total_carts) * 100
    
    data = {
        'behavior_by_action': list(behavior_by_action),
        'top_searches': list(top_searches),
        'cart_abandonment_rate': float(cart_abandonment_rate),
        'recovered_carts': recovered_carts
    }
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_top_products(request):
    """Get top products based on various metrics"""
    # Date range from query params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Top selling by quantity
    top_by_quantity = Order.objects.filter(
        created_at__date__range=[start_date, end_date],
        payment_status='paid'
    ).values(
        'items__product__id', 'items__product__name', 'items__product__price', 'items__product__image'
    ).annotate(
        total_sold=Sum('items__quantity'),
        total_revenue=Sum(F('items__quantity') * F('items__price'))
    ).order_by('-total_sold')[:10]
    
    # Top by revenue
    top_by_revenue = Order.objects.filter(
        created_at__date__range=[start_date, end_date],
        payment_status='paid'
    ).values(
        'items__product__id', 'items__product__name', 'items__product__price', 'items__product__image'
    ).annotate(
        total_revenue=Sum(F('items__quantity') * F('items__price'))
    ).order_by('-total_revenue')[:10]
    
    data = {
        'top_by_quantity': list(top_by_quantity),
        'top_by_revenue': list(top_by_revenue)
    }
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_top_customers(request):
    """Get top customers based on spending"""
    # Date range from query params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Top customers by total spending
    top_customers = Order.objects.filter(
        created_at__date__range=[start_date, end_date],
        payment_status='paid'
    ).values(
        'user__id', 'user__email', 'user__first_name', 'user__last_name'
    ).annotate(
        total_spent=Sum('total_amount'),
        total_orders=Count('id')
    ).order_by('-total_spent')[:10]
    
    data = {
        'top_customers': list(top_customers)
    }
    
    return Response(data)