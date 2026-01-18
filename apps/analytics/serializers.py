from rest_framework import serializers
from .models import RevenueSnapshot, ProductView, UserSearch, CartAbandonment, UserBehavior

class RevenueSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueSnapshot
        fields = [
            'id', 'date', 'total_revenue', 'total_orders', 'total_customers', 'avg_order_value',
            'cash_on_delivery', 'card_payments', 'mobile_money', 'other_payments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductView
        fields = ['id', 'product', 'user', 'session_key', 'viewed_at', 'ip_address']
        read_only_fields = ['id', 'viewed_at']


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSearch
        fields = ['id', 'query', 'user', 'session_key', 'searched_at', 'ip_address', 'results_count']
        read_only_fields = ['id', 'searched_at']


class CartAbandonmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartAbandonment
        fields = [
            'id', 'user', 'session_key', 'cart_items_count', 'cart_total',
            'abandoned_at', 'ip_address', 'recovered'
        ]
        read_only_fields = ['id', 'abandoned_at']


class UserBehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBehavior
        fields = [
            'id', 'user', 'session_key', 'action', 'target_id', 'target_type',
            'metadata', 'timestamp', 'ip_address'
        ]
        read_only_fields = ['id', 'timestamp']


class RevenueAnalyticsSerializer(serializers.Serializer):
    """Serializer for revenue analytics data"""
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    avg_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    revenue_by_payment_method = serializers.DictField()
    revenue_trend = serializers.ListField(child=serializers.DictField())


class UserAnalyticsSerializer(serializers.Serializer):
    """Serializer for user analytics data"""
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    user_growth_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


class ProductAnalyticsSerializer(serializers.Serializer):
    """Serializer for product analytics data"""
    top_selling_products = serializers.ListField(child=serializers.DictField())
    most_viewed_products = serializers.ListField(child=serializers.DictField())
    conversion_rates = serializers.DictField()