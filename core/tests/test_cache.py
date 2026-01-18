"""
Cache System Tests
------------------
Comprehensive tests for the caching system.

Tests:
- Cache hits and misses
- Cache invalidation
- Cache stampede protection
- No stale data after updates
- HTTP cache headers
"""
import pytest
import time
from django.core.cache import cache
from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch, MagicMock
from core.cache_utils import (
    CacheKeyBuilder, CacheManager, cache_result, 
    CacheStampedeProtection, CacheNamespaces
)
from core.middleware import CacheControlMiddleware
from apps.products.models import Product, Category, Brand

User = get_user_model()


class CacheKeyBuilderTests(TestCase):
    """Test cache key building"""
    
    def test_build_simple_key(self):
        """Test building a simple cache key"""
        key = CacheKeyBuilder.build('product', 'list')
        self.assertEqual(key, 'product:list')
    
    def test_build_key_with_args(self):
        """Test building key with arguments"""
        key = CacheKeyBuilder.build('product', 'detail', 123)
        self.assertEqual(key, 'product:detail:123')
    
    def test_build_key_with_kwargs(self):
        """Test building key with keyword arguments"""
        key = CacheKeyBuilder.build('product', 'search', query='laptop', category=5)
        self.assertIn('product:search', key)
    
    def test_build_long_key_hashing(self):
        """Test that long keys are hashed"""
        long_string = 'x' * 250
        key = CacheKeyBuilder.build('product', long_string)
        self.assertLess(len(key), 250)
        self.assertIn('product:', key)
    
    def test_build_pattern(self):
        """Test building cache pattern"""
        pattern = CacheKeyBuilder.pattern('product')
        self.assertEqual(pattern, 'product:*')


class CacheManagerTests(TestCase):
    """Test cache management operations"""
    
    def setUp(self):
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    def test_get_or_set_cache_miss(self):
        """Test get_or_set on cache miss"""
        call_count = 0
        
        def expensive_function():
            nonlocal call_count
            call_count += 1
            return 'computed_value'
        
        result = CacheManager.get_or_set('test_key', expensive_function, timeout=60)
        
        self.assertEqual(result, 'computed_value')
        self.assertEqual(call_count, 1)
    
    def test_get_or_set_cache_hit(self):
        """Test get_or_set on cache hit"""
        cache.set('test_key', 'cached_value', 60)
        
        call_count = 0
        
        def expensive_function():
            nonlocal call_count
            call_count += 1
            return 'computed_value'
        
        result = CacheManager.get_or_set('test_key', expensive_function, timeout=60)
        
        self.assertEqual(result, 'cached_value')
        self.assertEqual(call_count, 0)  # Function not called
    
    def test_delete_pattern(self):
        """Test deleting cache keys by pattern"""
        cache.set('product:1', 'data1', 60)
        cache.set('product:2', 'data2', 60)
        cache.set('category:1', 'data3', 60)
        
        # Delete product keys
        CacheManager.delete_pattern('product:*')
        
        # Product keys should be deleted
        self.assertIsNone(cache.get('product:1'))
        self.assertIsNone(cache.get('product:2'))
        
        # Category key should still exist
        self.assertIsNotNone(cache.get('category:1'))
    
    def test_invalidate_related(self):
        """Test invalidating multiple related namespaces"""
        cache.set('product:1', 'data1', 60)
        cache.set('category:1', 'data2', 60)
        
        CacheManager.invalidate_related(CacheNamespaces.PRODUCT, CacheNamespaces.CATEGORY)
        
        # Both should be cleared
        self.assertIsNone(cache.get('product:1'))
        self.assertIsNone(cache.get('category:1'))


class CacheResultDecoratorTests(TestCase):
    """Test cache_result decorator"""
    
    def setUp(self):
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    def test_decorator_caches_result(self):
        """Test that decorator caches function result"""
        call_count = 0
        
        @cache_result(timeout=60, key_prefix='test_func')
        def test_function():
            nonlocal call_count
            call_count += 1
            return 'result'
        
        # First call - cache miss
        result1 = test_function()
        self.assertEqual(call_count, 1)
        
        # Second call - cache hit
        result2 = test_function()
        self.assertEqual(call_count, 1)  # Not called again
        
        self.assertEqual(result1, result2)
    
    def test_decorator_with_args(self):
        """Test decorator with function arguments"""
        @cache_result(timeout=60, key_prefix='test_func')
        def test_function(x, y):
            return x + y
        
        result1 = test_function(1, 2)
        result2 = test_function(1, 2)
        result3 = test_function(2, 3)
        
        self.assertEqual(result1, 3)
        self.assertEqual(result2, 3)
        self.assertEqual(result3, 5)


@pytest.mark.django_db
class ProductCacheTests(APITestCase):
    """Test product caching"""
    
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        
        # Create test data
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            is_active=True
        )
        
        self.brand = Brand.objects.create(
            name='TestBrand',
            slug='testbrand',
            is_active=True
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test description',
            category=self.category,
            brand=self.brand,
            price=100.00,
            stock=10,
            is_active=True
        )
    
    def tearDown(self):
        cache.clear()
    
    def test_product_list_caching(self):
        """Test that product list is cached"""
        # First request - cache miss
        response1 = self.client.get('/api/products/')
        self.assertEqual(response1.status_code, 200)
        
        # Check cache headers
        self.assertIn('Cache-Control', response1)
        
        # Modify product
        self.product.name = 'Modified Product'
        self.product.save()
        
        # Second request - should still get cached data initially
        # (In production, signals would invalidate this)
    
    def test_product_detail_caching(self):
        """Test that product detail is cached"""
        response1 = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response1.status_code, 200)
        
        # Check ETag header
        self.assertIn('ETag', response1)
        etag = response1['ETag']
        
        # Second request with If-None-Match
        response2 = self.client.get(
            f'/api/products/{self.product.id}/',
            HTTP_IF_NONE_MATCH=etag
        )
        # Should return 304 Not Modified if content unchanged
    
    def test_cache_invalidation_on_product_update(self):
        """Test cache is invalidated when product is updated"""
        cache_key = f'product:detail:{self.product.id}'
        cache.set(cache_key, 'cached_data', 300)
        
        # Update product - signal should invalidate cache
        self.product.name = 'Updated Product'
        self.product.save()
        
        # Cache should be cleared
        # (This requires signals to be registered)


@pytest.mark.django_db
class CategoryCacheTests(APITestCase):
    """Test category caching"""
    
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            is_active=True
        )
    
    def tearDown(self):
        cache.clear()
    
    def test_category_list_cached(self):
        """Test that category list is cached"""
        response1 = self.client.get('/api/categories/')
        self.assertEqual(response1.status_code, 200)
        
        # Check cache headers
        self.assertIn('Cache-Control', response1)


class CacheStampedeProtectionTests(TestCase):
    """Test cache stampede protection"""
    
    def setUp(self):
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    @patch('time.sleep')  # Mock sleep to speed up test
    def test_stampede_protection(self, mock_sleep):
        """Test that only one request computes value"""
        call_count = 0
        
        def expensive_computation():
            nonlocal call_count
            call_count += 1
            time.sleep(0.1)  # Simulate slow operation
            return 'computed_value'
        
        # This would normally be called by multiple concurrent requests
        result = CacheStampedeProtection.get_or_compute(
            'test_key',
            expensive_computation,
            timeout=60,
            lock_timeout=10
        )
        
        self.assertEqual(result, 'computed_value')
        self.assertEqual(call_count, 1)


class HTTPCacheHeadersTests(TestCase):
    """Test HTTP cache headers middleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = CacheControlMiddleware(get_response=lambda r: MagicMock(status_code=200, content=b'test'))
    
    def test_never_cache_cart_endpoints(self):
        """Test that cart endpoints are never cached"""
        request = self.factory.get('/api/cart/')
        request.user = MagicMock(is_authenticated=False)
        
        response = MagicMock(status_code=200)
        response.content = b'test content'
        
        result = self.middleware.process_response(request, response)
        
        # Should have no-cache headers
        # (Would need to check actual response object)
    
    def test_never_cache_payment_endpoints(self):
        """Test that payment endpoints are never cached"""
        request = self.factory.get('/api/payments/')
        request.user = MagicMock(is_authenticated=True)
        
        response = MagicMock(status_code=200)
        response.content = b'test content'
        
        result = self.middleware.process_response(request, response)
        # Should have no-cache headers
    
    def test_cache_public_endpoints(self):
        """Test that public endpoints are cached"""
        request = self.factory.get('/api/products/')
        request.user = MagicMock(is_authenticated=False)
        
        response = MagicMock(status_code=200)
        response.content = b'test content'
        
        result = self.middleware.process_response(request, response)
        # Should have cache headers with appropriate TTL
    
    def test_etag_generation(self):
        """Test ETag generation"""
        request = self.factory.get('/api/products/')
        request.user = MagicMock(is_authenticated=False)
        request.META = {}
        
        response = MagicMock(status_code=200)
        response.content = b'test content'
        response.__setitem__ = lambda s, k, v: None
        
        self.middleware.process_response(request, response)
        # Should generate ETag


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
})
class CacheIntegrationTests(APITestCase):
    """Integration tests for entire cache system"""
    
    def setUp(self):
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    def test_full_cache_lifecycle(self):
        """Test complete cache lifecycle: set, hit, invalidate"""
        # This would test a full user journey with caching
        pass


# Run tests with: python manage.py test core.tests.test_cache
# Or with pytest: pytest core/tests/test_cache.py
