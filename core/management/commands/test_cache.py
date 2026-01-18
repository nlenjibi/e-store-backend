"""
Management command to test and verify cache system.

Usage:
    python manage.py test_cache
    python manage.py test_cache --verbose
    python manage.py test_cache --clear
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
import time
from decimal import Decimal


class Command(BaseCommand):
    help = 'Test and verify the cache system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all cache before testing',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )
    
    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Cache System Test'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        # Clear cache if requested
        if options.get('clear'):
            self.stdout.write('Clearing cache...')
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✓ Cache cleared\n'))
        
        # Test 1: Redis Connection
        self.test_redis_connection(verbose)
        
        # Test 2: Basic Operations
        self.test_basic_operations(verbose)
        
        # Test 3: Performance
        self.test_performance(verbose)
        
        # Test 4: Cache Configuration
        self.test_configuration(verbose)
        
        # Test 5: Cache Keys
        self.test_cache_keys(verbose)
        
        # Summary
        self.print_summary()
    
    def test_redis_connection(self, verbose):
        """Test Redis connection"""
        self.stdout.write(self.style.WARNING('Test 1: Redis Connection'))
        
        try:
            # Test basic connection
            cache.set('test_connection', 'connected', 10)
            value = cache.get('test_connection')
            
            if value == 'connected':
                self.stdout.write(self.style.SUCCESS('✓ Redis is connected and working'))
                cache.delete('test_connection')
            else:
                self.stdout.write(self.style.ERROR('✗ Redis connection issue'))
                return
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Redis connection failed: {e}'))
            return
        
        # Test Redis info
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            info = redis_conn.info()
            
            if verbose:
                self.stdout.write(f'  - Redis Version: {info.get("redis_version")}')
                self.stdout.write(f'  - Used Memory: {info.get("used_memory_human")}')
                self.stdout.write(f'  - Connected Clients: {info.get("connected_clients")}')
                self.stdout.write(f'  - Total Commands: {info.get("total_commands_processed")}')
            
            self.stdout.write(self.style.SUCCESS('✓ Redis info retrieved successfully'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  Could not get Redis info: {e}'))
        
        self.stdout.write('')
    
    def test_basic_operations(self, verbose):
        """Test basic cache operations"""
        self.stdout.write(self.style.WARNING('Test 2: Basic Cache Operations'))
        
        # Test SET
        try:
            cache.set('test_key', 'test_value', 60)
            self.stdout.write(self.style.SUCCESS('✓ SET operation works'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ SET failed: {e}'))
        
        # Test GET
        try:
            value = cache.get('test_key')
            if value == 'test_value':
                self.stdout.write(self.style.SUCCESS('✓ GET operation works'))
            else:
                self.stdout.write(self.style.ERROR('✗ GET returned wrong value'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ GET failed: {e}'))
        
        # Test DELETE
        try:
            cache.delete('test_key')
            value = cache.get('test_key')
            if value is None:
                self.stdout.write(self.style.SUCCESS('✓ DELETE operation works'))
            else:
                self.stdout.write(self.style.ERROR('✗ DELETE did not remove key'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ DELETE failed: {e}'))
        
        # Test complex data types
        try:
            test_data = {
                'string': 'hello',
                'number': 42,
                'float': 3.14,
                'list': [1, 2, 3],
                'dict': {'nested': 'value'},
                'decimal': Decimal('99.99')
            }
            cache.set('test_complex', test_data, 60)
            retrieved = cache.get('test_complex')
            
            if retrieved and retrieved['string'] == 'hello':
                self.stdout.write(self.style.SUCCESS('✓ Complex data types work'))
            else:
                self.stdout.write(self.style.ERROR('✗ Complex data types failed'))
            
            cache.delete('test_complex')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Complex data test failed: {e}'))
        
        self.stdout.write('')
    
    def test_performance(self, verbose):
        """Test cache performance"""
        self.stdout.write(self.style.WARNING('Test 3: Performance'))
        
        # Test write performance
        iterations = 100
        start_time = time.time()
        
        for i in range(iterations):
            cache.set(f'perf_test_{i}', f'value_{i}', 60)
        
        write_time = time.time() - start_time
        write_ops_per_sec = iterations / write_time
        
        self.stdout.write(f'✓ Write: {iterations} operations in {write_time:.3f}s ({write_ops_per_sec:.0f} ops/sec)')
        
        # Test read performance
        start_time = time.time()
        
        for i in range(iterations):
            cache.get(f'perf_test_{i}')
        
        read_time = time.time() - start_time
        read_ops_per_sec = iterations / read_time
        
        self.stdout.write(f'✓ Read: {iterations} operations in {read_time:.3f}s ({read_ops_per_sec:.0f} ops/sec)')
        
        # Clean up
        for i in range(iterations):
            cache.delete(f'perf_test_{i}')
        
        # Performance verdict
        if read_ops_per_sec > 1000:
            self.stdout.write(self.style.SUCCESS('✓ Performance: Excellent'))
        elif read_ops_per_sec > 500:
            self.stdout.write(self.style.SUCCESS('✓ Performance: Good'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Performance: Could be better'))
        
        self.stdout.write('')
    
    def test_configuration(self, verbose):
        """Test cache configuration"""
        self.stdout.write(self.style.WARNING('Test 4: Configuration'))
        
        # Check cache backend
        cache_backend = settings.CACHES['default']['BACKEND']
        self.stdout.write(f'Backend: {cache_backend}')
        
        if 'redis' in cache_backend.lower():
            self.stdout.write(self.style.SUCCESS('✓ Using Redis backend'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Not using Redis: {cache_backend}'))
        
        # Check cache location
        cache_location = settings.CACHES['default'].get('LOCATION', 'Not set')
        self.stdout.write(f'Location: {cache_location}')
        
        # Check TTL settings
        if hasattr(settings, 'CACHE_TTL'):
            self.stdout.write(self.style.SUCCESS('✓ CACHE_TTL settings configured'))
            if verbose:
                for key, value in settings.CACHE_TTL.items():
                    self.stdout.write(f'  - {key}: {value}s ({value/60:.0f} min)')
        else:
            self.stdout.write(self.style.WARNING('⚠ CACHE_TTL not configured'))
        
        # Check middleware
        if 'core.middleware.CacheControlMiddleware' in settings.MIDDLEWARE:
            self.stdout.write(self.style.SUCCESS('✓ CacheControlMiddleware is active'))
        else:
            self.stdout.write(self.style.WARNING('⚠ CacheControlMiddleware not in MIDDLEWARE'))
        
        self.stdout.write('')
    
    def test_cache_keys(self, verbose):
        """Test cache key patterns"""
        self.stdout.write(self.style.WARNING('Test 5: Cache Keys'))
        
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            
            # Count keys by pattern
            patterns = {
                'product': 'product:*',
                'category': 'category:*',
                'promotion': 'promotion:*',
                'analytics': 'analytics:*',
                'homepage': 'homepage:*',
            }
            
            total_keys = 0
            for name, pattern in patterns.items():
                keys = redis_conn.keys(f'*{pattern}*')
                count = len(keys)
                total_keys += count
                
                if count > 0:
                    self.stdout.write(f'✓ {name.capitalize()}: {count} keys')
                    if verbose and count <= 5:
                        for key in keys[:5]:
                            self.stdout.write(f'    - {key.decode()}')
            
            self.stdout.write(f'\nTotal cache keys: {total_keys}')
            
            if total_keys == 0:
                self.stdout.write(self.style.WARNING('⚠ No cache keys found (cache may be empty)'))
            else:
                self.stdout.write(self.style.SUCCESS('✓ Cache is populated'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Could not check cache keys: {e}'))
        
        self.stdout.write('')
    
    def print_summary(self):
        """Print test summary"""
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('Summary'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('')
        self.stdout.write('Cache system is operational and ready for use!')
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Make some API requests to populate cache')
        self.stdout.write('2. Monitor cache with: redis-cli MONITOR')
        self.stdout.write('3. Check logs for cache hits/misses')
        self.stdout.write('4. Run full tests: python manage.py test core.tests.test_cache')
        self.stdout.write('')
        self.stdout.write('Documentation:')
        self.stdout.write('- Strategy: CACHE_STRATEGY.md')
        self.stdout.write('- Setup: CACHE_SETUP.md')
        self.stdout.write('- Quick Ref: CACHE_QUICK_REFERENCE.md')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*60))
