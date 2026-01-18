"""Tags models for the e-commerce platform."""
from django.db import models
from django.utils.text import slugify
import uuid


class Tag(models.Model):
    """Product tag model."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, db_index=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6', help_text='Hex color code')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class ProductTag(models.Model):
    """Many-to-many relationship between products and tags."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='product_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='tagged_products')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('product', 'tag')
        ordering = ['added_at']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['tag']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.tag.name}"

