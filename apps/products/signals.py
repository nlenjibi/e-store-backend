"""Signals for the products app."""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Avg
from .models import Product, ProductReview


@receiver(post_save, sender=ProductReview)
def update_product_rating(sender, instance, created, **kwargs):
    """Update product rating when a review is saved."""
    if created or kwargs.get('update_fields') is None or 'rating' in kwargs.get('update_fields', set()):
        product = instance.product
        avg_rating = ProductReview.objects.filter(
            product=product, 
            is_approved=True
        ).aggregate(Avg('rating'))['rating__avg']
        
        if avg_rating:
            product.rating = avg_rating
            product.num_reviews = ProductReview.objects.filter(
                product=product, 
                is_approved=True
            ).count()
            product.save(update_fields=['rating', 'num_reviews'])