"""
Cache Invalidation Signals
---------------------------
Automatic cache invalidation when models are updated.

This ensures data consistency by clearing relevant caches
when database records change.
"""
import logging
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from core.cache_utils import CacheManager, CacheNamespaces

logger = logging.getLogger(__name__)


# ====================
# PRODUCTS CACHE INVALIDATION
# ====================

@receiver(post_save, sender='products.Product')
@receiver(post_delete, sender='products.Product')
def invalidate_product_cache(sender, instance, **kwargs):
    """
    Invalidate product-related caches when a product is modified.
    
    Triggered on:
    - Product create/update/delete
    """
    logger.info(f"Invalidating product cache for: {instance.id}")
    
    # Invalidate all product-related caches
    CacheManager.invalidate_related(
        CacheNamespaces.PRODUCT,
        CacheNamespaces.HOMEPAGE,
        CacheNamespaces.ANALYTICS
    )
    
    # Invalidate specific product cache
    cache.delete(f"product:detail:{instance.id}")
    
    # If product is in a category, invalidate category caches
    if hasattr(instance, 'category') and instance.category:
        cache.delete(f"product:category:{instance.category.id}")
        CacheManager.invalidate_related(CacheNamespaces.CATEGORY)


@receiver(post_save, sender='products.ProductImage')
@receiver(post_delete, sender='products.ProductImage')
def invalidate_product_image_cache(sender, instance, **kwargs):
    """Invalidate cache when product images change"""
    if hasattr(instance, 'product') and instance.product:
        logger.info(f"Invalidating cache for product {instance.product.id} (image change)")
        cache.delete(f"product:detail:{instance.product.id}")
        CacheManager.delete_pattern(f"product:list:*")


@receiver(post_save, sender='products.ProductReview')
@receiver(post_delete, sender='products.ProductReview')
def invalidate_product_review_cache(sender, instance, **kwargs):
    """Invalidate cache when reviews change"""
    if hasattr(instance, 'product') and instance.product:
        logger.info(f"Invalidating cache for product {instance.product.id} (review change)")
        cache.delete(f"product:detail:{instance.product.id}")
        cache.delete("top_rated_products")


# ====================
# CATEGORY CACHE INVALIDATION
# ====================

@receiver(post_save, sender='products.Category')
@receiver(post_delete, sender='products.Category')
def invalidate_category_cache(sender, instance, **kwargs):
    """
    Invalidate category-related caches when a category is modified.
    """
    logger.info(f"Invalidating category cache for: {instance.id}")
    
    # Invalidate all category caches
    CacheManager.invalidate_related(
        CacheNamespaces.CATEGORY,
        CacheNamespaces.PRODUCT,
        CacheNamespaces.HOMEPAGE
    )
    
    # Invalidate specific category cache
    cache.delete(f"category:detail:{instance.id}")
    cache.delete("category:tree")


@receiver(post_save, sender='products.Brand')
@receiver(post_delete, sender='products.Brand')
def invalidate_brand_cache(sender, instance, **kwargs):
    """Invalidate cache when brands change"""
    logger.info(f"Invalidating brand cache for: {instance.id}")
    CacheManager.delete_pattern("brand:*")
    CacheManager.invalidate_related(CacheNamespaces.PRODUCT)


# ====================
# PROMOTIONS CACHE INVALIDATION
# ====================

@receiver(post_save, sender='promotions.Coupon')
@receiver(post_delete, sender='promotions.Coupon')
def invalidate_coupon_cache(sender, instance, **kwargs):
    """Invalidate cache when coupons change"""
    logger.info(f"Invalidating coupon cache for: {instance.code}")
    CacheManager.invalidate_related(
        CacheNamespaces.PROMOTION,
        CacheNamespaces.HOMEPAGE
    )


@receiver(post_save, sender='promotions.FlashSale')
@receiver(post_delete, sender='promotions.FlashSale')
def invalidate_flash_sale_cache(sender, instance, **kwargs):
    """Invalidate cache when flash sales change"""
    logger.info(f"Invalidating flash sale cache for: {instance.id}")
    CacheManager.invalidate_related(
        CacheNamespaces.PROMOTION,
        CacheNamespaces.HOMEPAGE
    )
    
    # Also invalidate the affected product
    if hasattr(instance, 'product') and instance.product:
        cache.delete(f"product:detail:{instance.product.id}")


@receiver(post_save, sender='promotions.Banner')
@receiver(post_delete, sender='promotions.Banner')
def invalidate_banner_cache(sender, instance, **kwargs):
    """Invalidate cache when banners change"""
    logger.info(f"Invalidating banner cache for: {instance.id}")
    CacheManager.invalidate_related(
        CacheNamespaces.PROMOTION,
        CacheNamespaces.HOMEPAGE
    )


# ====================
# ADMIN-TRIGGERED INVALIDATION
# ====================

@receiver(post_save, sender='products.Product')
def invalidate_admin_changes(sender, instance, **kwargs):
    """
    Extra invalidation for admin changes.
    
    When admin updates featured/trending status, ensure
    those specific caches are cleared.
    """
    if kwargs.get('update_fields'):
        updated_fields = kwargs['update_fields']
        
        if 'is_featured' in updated_fields:
            logger.info("Invalidating featured products cache")
            cache.delete("featured_products")
            cache.delete("homepage:featured")
        
        if 'is_trending' in updated_fields:
            logger.info("Invalidating trending products cache")
            cache.delete("trending_products")
        
        if 'is_active' in updated_fields:
            logger.info("Invalidating product lists (active status changed)")
            CacheManager.delete_pattern("product:list:*")


# ====================
# ORDERS CACHE INVALIDATION (ANALYTICS)
# ====================

@receiver(post_save, sender='orders.Order')
def invalidate_order_analytics_cache(sender, instance, **kwargs):
    """
    Invalidate analytics caches when orders change.
    
    Note: Only invalidate analytics, never cache order data itself.
    """
    logger.info(f"Invalidating analytics cache (order {instance.id} changed)")
    CacheManager.invalidate_related(CacheNamespaces.ANALYTICS)


# ====================
# M2M RELATIONSHIP INVALIDATION
# ====================

@receiver(m2m_changed)
def invalidate_m2m_cache(sender, instance, action, **kwargs):
    """
    Invalidate cache when many-to-many relationships change.
    
    Examples:
    - Product tags
    - Banner products/categories
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        model_name = instance.__class__.__name__.lower()
        logger.info(f"Invalidating cache for {model_name} (M2M change)")
        
        if model_name == 'product':
            cache.delete(f"product:detail:{instance.id}")
            CacheManager.delete_pattern("product:list:*")
        
        elif model_name == 'banner':
            CacheManager.invalidate_related(CacheNamespaces.PROMOTION, CacheNamespaces.HOMEPAGE)


# ====================
# SELECTIVE CACHE WARMING
# ====================

@receiver(post_save, sender='products.Product')
def warm_featured_cache(sender, instance, created, **kwargs):
    """
    Warm cache for featured products when they're marked as featured.
    
    This is optional but improves UX by pre-loading frequently accessed data.
    """
    if not created and kwargs.get('update_fields') and 'is_featured' in kwargs['update_fields']:
        if instance.is_featured and instance.is_active:
            logger.info("Warming featured products cache")
            
            # Import here to avoid circular imports
            from apps.products.models import Product
            from apps.products.serializers import ProductListSerializer
            
            # Pre-warm the cache
            products = Product.objects.filter(
                is_active=True,
                is_deleted=False,
                is_featured=True
            )[:10]
            
            serializer = ProductListSerializer(products, many=True)
            cache.set('featured_products', serializer.data, 300)
