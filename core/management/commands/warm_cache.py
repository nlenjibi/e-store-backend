"""
Management command to warm cache with initial data.

Usage:
    python manage.py warm_cache
    python manage.py warm_cache --all
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings


class Command(BaseCommand):
    help = 'Warm cache with initial data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Warm all caches',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Cache Warming'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        warm_all = options.get('all', False)
        
        # Warm featured products
        self.warm_featured_products()
        
        # Warm categories
        self.warm_categories()
        
        if warm_all:
            # Warm trending products
            self.warm_trending_products()
            
            # Warm top-rated products
            self.warm_top_rated_products()
            
            # Warm active promotions
            self.warm_promotions()
        
        self.stdout.write(self.style.SUCCESS('\n✓ Cache warming complete!\n'))
    
    def warm_featured_products(self):
        """Warm featured products cache"""
        self.stdout.write('Warming featured products...')
        
        try:
            from apps.products.models import Product
            from apps.products.serializers import ProductListSerializer
            
            products = Product.objects.filter(
                is_active=True,
                is_deleted=False,
                is_featured=True
            )[:10]
            
            serializer = ProductListSerializer(products, many=True)
            cache.set('featured_products', serializer.data, settings.CACHE_TTL['SHORT'])
            
            self.stdout.write(self.style.SUCCESS(f'✓ Cached {len(products)} featured products'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed: {e}'))
    
    def warm_categories(self):
        """Warm categories cache"""
        self.stdout.write('Warming categories...')
        
        try:
            from apps.products.models import Category
            from apps.products.serializers import CategorySerializer
            
            categories = Category.objects.filter(is_active=True, is_deleted=False)
            serializer = CategorySerializer(categories, many=True)
            cache.set('category:list', serializer.data, settings.CACHE_TTL['MEDIUM'])
            
            self.stdout.write(self.style.SUCCESS(f'✓ Cached {len(categories)} categories'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed: {e}'))
    
    def warm_trending_products(self):
        """Warm trending products cache"""
        self.stdout.write('Warming trending products...')
        
        try:
            from apps.products.models import Product
            from apps.products.serializers import ProductListSerializer
            
            products = Product.objects.filter(
                is_active=True,
                is_deleted=False,
                is_trending=True
            ).order_by('-rating')[:10]
            
            serializer = ProductListSerializer(products, many=True)
            cache.set('trending_products', serializer.data, settings.CACHE_TTL['SHORT'])
            
            self.stdout.write(self.style.SUCCESS(f'✓ Cached {len(products)} trending products'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed: {e}'))
    
    def warm_top_rated_products(self):
        """Warm top-rated products cache"""
        self.stdout.write('Warming top-rated products...')
        
        try:
            from apps.products.models import Product
            from apps.products.serializers import ProductListSerializer
            
            products = Product.objects.filter(
                is_active=True,
                is_deleted=False
            ).order_by('-rating')[:10]
            
            serializer = ProductListSerializer(products, many=True)
            cache.set('top_rated_products', serializer.data, settings.CACHE_TTL['SHORT'])
            
            self.stdout.write(self.style.SUCCESS(f'✓ Cached {len(products)} top-rated products'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed: {e}'))
    
    def warm_promotions(self):
        """Warm promotions cache"""
        self.stdout.write('Warming promotions...')
        
        try:
            from django.utils import timezone
            from apps.promotions.models import Coupon, FlashSale, Banner
            from apps.promotions.serializers import CouponSerializer, FlashSaleSerializer, BannerSerializer
            
            now = timezone.now()
            
            # Active coupons
            coupons = Coupon.objects.filter(
                is_active=True,
                valid_from__lte=now,
                valid_until__gte=now
            )
            coupon_serializer = CouponSerializer(coupons, many=True)
            cache.set('active_coupons', coupon_serializer.data, settings.CACHE_TTL['SHORT'])
            
            # Active flash sales
            flash_sales = FlashSale.objects.filter(
                is_active=True,
                start_time__lte=now,
                end_time__gte=now
            ).select_related('product')
            flash_sale_serializer = FlashSaleSerializer(flash_sales, many=True)
            cache.set('active_flash_sales', flash_sale_serializer.data, settings.CACHE_TTL['SHORT'])
            
            # Active banners
            banners = Banner.objects.filter(
                is_active=True,
                start_date__lte=now,
                end_date__gte=now
            ).prefetch_related('products', 'categories')
            banner_serializer = BannerSerializer(banners, many=True)
            cache.set('active_banners', banner_serializer.data, settings.CACHE_TTL['SHORT'])
            
            self.stdout.write(self.style.SUCCESS(
                f'✓ Cached {len(coupons)} coupons, {len(flash_sales)} flash sales, {len(banners)} banners'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed: {e}'))
