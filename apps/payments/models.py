from django.db import models
from django.contrib.auth import get_user_model
from apps.orders.models import Order
from decimal import Decimal
import uuid

User = get_user_model()

class PaymentGateway(models.Model):
    """Supported payment gateways"""
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict)  # Store API keys and config
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name

    class Meta:
        db_table = 'payment_gateways'


class Transaction(models.Model):
    """Payment transaction records"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    TRANSACTION_TYPES = [
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('verification', 'Verification'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='payment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=100, unique=True)  # Gateway reference
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Gateway-specific data
    gateway_response = models.JSONField(default=dict)  # Raw response from gateway
    gateway_data = models.JSONField(default=dict)  # Additional gateway data
    
    # Metadata
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.reference} - {self.amount} ({self.status})"

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['order']),
            models.Index(fields=['reference']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]


class Refund(models.Model):
    """Refund records"""
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='refunds')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    reason = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Gateway-specific refund data
    gateway_refund_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(default=dict)
    
    # Metadata
    notes = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund {self.id} - {self.requested_amount}"

    class Meta:
        db_table = 'refunds'
        ordering = ['-requested_at']