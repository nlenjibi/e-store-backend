from django.db import models
from apps.products.models import Product, Category
from decimal import Decimal
from django.utils import timezone

class Coupon(models.Model):
    """Discount coupons"""
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(null=True, blank=True)  # Total usage limit
    usage_limit_per_user = models.PositiveIntegerField(null=True, blank=True)  # Per user limit
    used_count = models.PositiveIntegerField(default=0)  # Track usage
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Minimum order amount
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Specific products/categories (optional)
    products = models.ManyToManyField(Product, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_valid(self):
        """Check if coupon is currently valid"""
        now = timezone.now()
        return (self.is_active and 
                self.valid_from <= now <= self.valid_until and
                (self.usage_limit is None or self.used_count < self.usage_limit))

    def is_valid_for_user(self, user):
        """Check if coupon is valid for a specific user"""
        # Check general validity
        if not self.is_valid:
            return False
        
        # Check if user has exceeded usage limit
        if self.usage_limit_per_user:
            from apps.auth.models import User
            # In a real app, we'd track user-specific usage
            pass  # Simplified for now
        
        return True

    def calculate_discount(self, order_total):
        """Calculate discount amount for an order total"""
        if not self.is_valid:
            return Decimal('0.00')
        
        if self.discount_type == 'percentage':
            return min(order_total * (self.discount_value / 100), order_total)
        else:  # fixed
            return min(self.discount_value, order_total)

    class Meta:
        db_table = 'coupons'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['valid_from']),
            models.Index(fields=['valid_until']),
        ]


class FlashSale(models.Model):
    """Time-bound flash sales"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='flash_sales')
    name = models.CharField(max_length=200)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Limitations
    max_quantity = models.PositiveIntegerField()  # Total quantity available for sale
    quantity_sold = models.PositiveIntegerField(default=0)  # Track how many sold
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.discount_percentage}% off"

    @property
    def is_active_now(self):
        """Check if flash sale is currently active"""
        now = timezone.now()
        return (self.is_active and 
                self.start_time <= now <= self.end_time and
                self.quantity_sold < self.max_quantity)

    @property
    def time_remaining(self):
        """Get time remaining in the flash sale"""
        if self.end_time:
            now = timezone.now()
            if now < self.end_time:
                return self.end_time - now
        return None

    @property
    def items_remaining(self):
        """Get number of items remaining in the flash sale"""
        return max(0, self.max_quantity - self.quantity_sold)

    @property
    def is_sold_out(self):
        """Check if flash sale is sold out"""
        return self.quantity_sold >= self.max_quantity

    class Meta:
        db_table = 'flash_sales'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['is_active']),
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
        ]


class Banner(models.Model):
    """Promotional banners"""
    POSITION_CHOICES = [
        ('top', 'Top of Page'),
        ('bottom', 'Bottom of Page'),
        ('sidebar', 'Sidebar'),
        ('carousel', 'Carousel'),
    ]

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    
    # Image and media
    image = models.ImageField(upload_to='banners/', null=True, blank=True)
    mobile_image = models.ImageField(upload_to='banners/mobile/', null=True, blank=True)
    background_color = models.CharField(max_length=7, default='#ffffff')  # Hex color
    
    # Link and positioning
    link_url = models.URLField(blank=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='carousel')
    order = models.PositiveIntegerField(default=0)  # For ordering multiple banners
    
    # Targeting
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Product/Category association
    products = models.ManyToManyField(Product, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def is_visible(self):
        """Check if banner is currently visible"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    class Meta:
        db_table = 'banners'
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['position']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]