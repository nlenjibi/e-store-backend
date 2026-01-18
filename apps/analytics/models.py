from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import Product
from apps.orders.models import Order
from decimal import Decimal
from django.utils import timezone

User = get_user_model()

class RevenueSnapshot(models.Model):
    """Daily revenue snapshot for analytics"""
    date = models.DateField(unique=True)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_customers = models.PositiveIntegerField(default=0)
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment method breakdown
    cash_on_delivery = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    card_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mobile_money = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Revenue {self.date}: {self.total_revenue}"

    class Meta:
        db_table = 'revenue_snapshots'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
        ]


class ProductView(models.Model):
    """Track product views for analytics"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='analytics_views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} viewed at {self.viewed_at}"

    class Meta:
        db_table = 'product_views'
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
            models.Index(fields=['viewed_at']),
        ]


class UserSearch(models.Model):
    """Track user searches for analytics"""
    query = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    searched_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    results_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Search: {self.query} at {self.searched_at}"

    class Meta:
        db_table = 'user_searches'
        ordering = ['-searched_at']
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
            models.Index(fields=['searched_at']),
        ]


class CartAbandonment(models.Model):
    """Track cart abandonment for analytics"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    cart_items_count = models.PositiveIntegerField()
    cart_total = models.DecimalField(max_digits=10, decimal_places=2)
    abandoned_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    recovered = models.BooleanField(default=False)  # Whether cart was recovered later

    def __str__(self):
        return f"Cart abandoned by {self.user or self.session_key} at {self.abandoned_at}"

    class Meta:
        db_table = 'cart_abandonments'
        ordering = ['-abandoned_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
            models.Index(fields=['abandoned_at']),
            models.Index(fields=['recovered']),
        ]


class UserBehavior(models.Model):
    """General user behavior tracking"""
    ACTION_CHOICES = [
        ('view_product', 'View Product'),
        ('add_to_cart', 'Add to Cart'),
        ('remove_from_cart', 'Remove from Cart'),
        ('checkout_start', 'Checkout Start'),
        ('checkout_complete', 'Checkout Complete'),
        ('search', 'Search'),
        ('login', 'Login'),
        ('register', 'Register'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_id = models.PositiveIntegerField(null=True, blank=True)  # ID of target object
    target_type = models.CharField(max_length=20, null=True, blank=True)  # Type of target object
    metadata = models.JSONField(default=dict)  # Additional data about the action
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.action} by {self.user or self.session_key} at {self.timestamp}"

    class Meta:
        db_table = 'user_behaviors'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
        ]