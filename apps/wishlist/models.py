"""Wishlist models for the e-commerce platform."""
from django.db import models
from django.utils import timezone
from apps.auth.models import User
from apps.products.models import Product
import uuid


class Wishlist(models.Model):
    """User wishlist model."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['user', '-added_at']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"
    
    @property
    def is_in_stock(self):
        """Check if wishlist product is in stock."""
        return self.product.is_in_stock
    
    @property
    def can_add_to_cart(self):
        """Check if product can be added to cart (in stock)."""
        return self.product.is_in_stock


class WishlistActivity(models.Model):
    """Track wishlist activities for analytics."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_activities')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_activities')
    action = models.CharField(max_length=20, choices=[
        ('ADDED', 'Added to wishlist'),
        ('REMOVED', 'Removed from wishlist'),
        ('MOVED_TO_CART', 'Moved to cart')
    ])
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.product.name}"
