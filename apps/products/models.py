"""Product models for the Smart E-Commerce platform."""
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.auth.models import User
import uuid


class Category(models.Model):
    """Product category model."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True, db_index=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Brand(models.Model):
    """Product brand model."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, db_index=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    sku = models.CharField(max_length=100, unique=True)  # Stock Keeping Unit
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)
    category = models.ForeignKey(Category, to_field='slug', on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    images = models.JSONField(default=list, blank=True, help_text='List of image URLs')  # Multiple image URLs
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, 
                                         validators=[MinValueValidator(0)], blank=True, null=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, 
                                          validators=[MinValueValidator(0), MaxValueValidator(100)], 
                                          blank=True, null=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, 
                                   validators=[MinValueValidator(0), MaxValueValidator(100)], 
                                   default=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=10)  # Minimum stock level before alert
    shipping_type = models.CharField(
        max_length=10,
        choices=[('STORE', 'In Store'), ('SHIP', 'Shipped')],
        default='SHIP',
        help_text='Fulfillment type: In Store pickup or Shipped'
    )
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)  # in kg
    dimensions = models.CharField(max_length=100, blank=True)  # e.g., "10x5x3 cm"
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=100, blank=True)
    warranty_period = models.PositiveIntegerField(blank=True, null=True)  # in months
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, 
                                 validators=[MinValueValidator(0), MaxValueValidator(5)])
    num_reviews = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['price']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.discount_price and self.price:
            self.discount_percent = ((self.price - self.discount_price) / self.price) * 100
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    @property
    def final_price(self):
        """Return the final price after discount."""
        if self.discount_price:
            return self.discount_price
        return self.price
    
    @property
    def is_in_stock(self):
        """Check if the product is in stock."""
        return self.stock_quantity > 0
    
    @property
    def stock_status(self):
        """Return stock status as a string."""
        if self.stock_quantity > 0:
            return 'IN_STOCK'
        return 'OUT_OF_STOCK'
    
    @property
    def is_low_stock(self):
        """Check if the product is at low stock level."""
        return self.stock_quantity <= self.min_stock_level
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage."""
        if self.price and self.discount_price:
            return ((self.price - self.discount_price) / self.price) * 100
        return 0


class ProductImage(models.Model):
    """Product image model - URL-based (no file uploads)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image_url = models.URLField(max_length=500, help_text='External image URL (CDN, S3, vendor URL)')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order']
        indexes = [
            models.Index(fields=['product', 'is_primary']),
        ]
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Image for {self.product.name}"


class ProductReview(models.Model):
    """Product review model."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.product.name} by {self.user.email}"


class ProductView(models.Model):
    """Model to track product views."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_views_log')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='product_views')
    session_key = models.CharField(max_length=40, blank=True)  # For anonymous users
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        indexes = [
            models.Index(fields=['product', 'timestamp']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"View of {self.product.name}"


class ProductSearch(models.Model):
    """Model to track product searches."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='searches')
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField()
    results_count = models.PositiveIntegerField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"Search: {self.query}"