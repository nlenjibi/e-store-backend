"""
Cache Utilities
---------------
Centralized cache management utilities for the e-commerce platform.

Features:
- Safe cache operations with graceful degradation
- Cache key generation and management
- Cache invalidation patterns
- Cache stampede protection
- Cache warming utilities
"""
import hashlib
import json
import logging
from functools import wraps
from typing import Any, Callable, Optional, List
from django.core.cache import cache
from django.conf import settings
from django.db.models import QuerySet

logger = logging.getLogger(__name__)


class CacheKeyBuilder:
    """Build consistent, namespaced cache keys"""
    
    @staticmethod
    def build(namespace: str, *args, **kwargs) -> str:
        """
        Build a cache key from namespace and arguments.
        
        Args:
            namespace: Primary namespace (e.g., 'product', 'category')
            *args: Positional arguments to include in key
            **kwargs: Keyword arguments to include in key
            
        Returns:
            A hashed cache key string
        """
        parts = [namespace]
        parts.extend(str(arg) for arg in args)
        
        if kwargs:
            # Sort kwargs for consistent hashing
            sorted_kwargs = sorted(kwargs.items())
            parts.append(json.dumps(sorted_kwargs, sort_keys=True))
        
        key_string = ":".join(parts)
        
        # Hash if key is too long
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{namespace}:{key_hash}"
        
        return key_string
    
    @staticmethod
    def pattern(namespace: str, pattern: str = "*") -> str:
        """Build a pattern for cache deletion"""
        return f"{namespace}:{pattern}"


class CacheManager:
    """High-level cache management operations"""
    
    @staticmethod
    def get_or_set(key: str, callable_func: Callable, timeout: Optional[int] = None) -> Any:
        """
        Get from cache or set if not exists.
        
        Args:
            key: Cache key
            callable_func: Function to call if cache miss
            timeout: Cache timeout in seconds
            
        Returns:
            Cached or freshly computed value
        """
        try:
            value = cache.get(key)
            
            if value is None:
                logger.debug(f"Cache miss: {key}")
                value = callable_func()
                
                if value is not None:
                    timeout = timeout or settings.CACHE_TTL['MEDIUM']
                    cache.set(key, value, timeout)
                    logger.debug(f"Cache set: {key} (TTL: {timeout}s)")
                    
            else:
                logger.debug(f"Cache hit: {key}")
                
            return value
            
        except Exception as e:
            logger.error(f"Cache error for key {key}: {e}")
            # Gracefully degrade - call function directly
            return callable_func()
    
    @staticmethod
    def delete_pattern(pattern: str) -> int:
        """
        Delete all cache keys matching pattern.
        
        Args:
            pattern: Pattern to match (e.g., 'product:*')
            
        Returns:
            Number of keys deleted
        """
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            
            # Get all keys matching pattern
            keys = redis_conn.keys(f"*{pattern}*")
            
            if keys:
                count = redis_conn.delete(*keys)
                logger.info(f"Deleted {count} cache keys matching pattern: {pattern}")
                return count
            
            return 0
            
        except Exception as e:
            logger.error(f"Error deleting cache pattern {pattern}: {e}")
            return 0
    
    @staticmethod
    def invalidate_related(*namespaces: str) -> None:
        """
        Invalidate multiple related cache namespaces.
        
        Args:
            *namespaces: Cache namespaces to invalidate
        """
        for namespace in namespaces:
            pattern = CacheKeyBuilder.pattern(namespace)
            CacheManager.delete_pattern(pattern)
    
    @staticmethod
    def warm_cache(key: str, callable_func: Callable, timeout: Optional[int] = None) -> None:
        """
        Pre-warm cache with data.
        
        Args:
            key: Cache key
            callable_func: Function to generate cache data
            timeout: Cache timeout
        """
        try:
            value = callable_func()
            if value is not None:
                timeout = timeout or settings.CACHE_TTL['MEDIUM']
                cache.set(key, value, timeout)
                logger.info(f"Cache warmed: {key}")
        except Exception as e:
            logger.error(f"Cache warming failed for {key}: {e}")


def cache_result(timeout: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator to cache function results.
    
    Usage:
        @cache_result(timeout=300, key_prefix="featured_products")
        def get_featured_products():
            return Product.objects.filter(featured=True)
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key from function name and arguments
            key_parts = [key_prefix or func.__name__]
            
            if args:
                key_parts.extend(str(arg) for arg in args)
            if kwargs:
                key_parts.append(json.dumps(kwargs, sort_keys=True))
            
            cache_key = CacheKeyBuilder.build(*key_parts)
            
            return CacheManager.get_or_set(
                cache_key,
                lambda: func(*args, **kwargs),
                timeout or settings.CACHE_TTL['MEDIUM']
            )
        
        return wrapper
    return decorator


def cache_queryset(timeout: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator specifically for caching QuerySet results.
    Automatically evaluates QuerySet to list.
    
    Usage:
        @cache_queryset(timeout=600, key_prefix="active_products")
        def get_active_products():
            return Product.objects.filter(is_active=True)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            key_parts = [key_prefix or func.__name__]
            
            if args:
                key_parts.extend(str(arg) for arg in args)
            if kwargs:
                key_parts.append(json.dumps(kwargs, sort_keys=True))
            
            cache_key = CacheKeyBuilder.build(*key_parts)
            
            def fetch_data():
                result = func(*args, **kwargs)
                # Convert QuerySet to list for caching
                if isinstance(result, QuerySet):
                    return list(result)
                return result
            
            return CacheManager.get_or_set(
                cache_key,
                fetch_data,
                timeout or settings.CACHE_TTL['MEDIUM']
            )
        
        return wrapper
    return decorator


class CacheStampedeProtection:
    """
    Protect against cache stampede (thundering herd problem).
    
    When cache expires and multiple requests hit at once, only one
    request will regenerate the cache while others wait.
    """
    
    @staticmethod
    def get_or_compute(key: str, compute_func: Callable, timeout: int = 300,
                       lock_timeout: int = 10) -> Any:
        """
        Get cached value or compute with stampede protection.
        
        Args:
            key: Cache key
            compute_func: Function to compute value
            timeout: Cache timeout
            lock_timeout: Lock timeout for computation
        """
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            
            # Try to get from cache
            value = cache.get(key)
            if value is not None:
                return value
            
            # Try to acquire lock
            lock_key = f"lock:{key}"
            lock_acquired = redis_conn.set(lock_key, "1", nx=True, ex=lock_timeout)
            
            if lock_acquired:
                try:
                    # This request will compute the value
                    value = compute_func()
                    if value is not None:
                        cache.set(key, value, timeout)
                    return value
                finally:
                    # Release lock
                    redis_conn.delete(lock_key)
            else:
                # Another request is computing, wait and retry
                import time
                for _ in range(lock_timeout * 2):
                    time.sleep(0.5)
                    value = cache.get(key)
                    if value is not None:
                        return value
                
                # Fallback: compute anyway if still no cache
                return compute_func()
                
        except Exception as e:
            logger.error(f"Stampede protection error for {key}: {e}")
            # Fallback to direct computation
            return compute_func()


# Pre-defined cache key patterns
class CacheKeys:
    """Standardized cache key patterns"""
    
    # Products
    PRODUCT_LIST = "product:list"
    PRODUCT_DETAIL = "product:detail:{id}"
    PRODUCT_FEATURED = "product:featured"
    PRODUCT_SEARCH = "product:search:{query}"
    PRODUCT_BY_CATEGORY = "product:category:{category_id}"
    
    # Categories
    CATEGORY_LIST = "category:list"
    CATEGORY_TREE = "category:tree"
    CATEGORY_DETAIL = "category:detail:{id}"
    
    # Promotions
    PROMOTION_ACTIVE = "promotion:active"
    PROMOTION_DETAIL = "promotion:detail:{id}"
    
    # Analytics
    ANALYTICS_DASHBOARD = "analytics:dashboard"
    ANALYTICS_SALES = "analytics:sales:{period}"
    ANALYTICS_POPULAR = "analytics:popular:{limit}"
    
    # Homepage
    HOMEPAGE_FEATURED = "homepage:featured"
    HOMEPAGE_DEALS = "homepage:deals"
    HOMEPAGE_CATEGORIES = "homepage:categories"
    
    # User-specific (include user_id in key)
    USER_RECOMMENDATIONS = "user:{user_id}:recommendations"
    USER_RECENTLY_VIEWED = "user:{user_id}:recent"


# Namespaces for batch invalidation
class CacheNamespaces:
    """Cache namespaces for invalidation"""
    PRODUCT = "product"
    CATEGORY = "category"
    PROMOTION = "promotion"
    ANALYTICS = "analytics"
    HOMEPAGE = "homepage"
    USER = "user"
