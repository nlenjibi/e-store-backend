"""
URL Configuration
-----------------
Main URL routing for the E-Commerce platform.

API Structure:
- /api/auth/          - Authentication & user management
- /api/products/      - Products, categories, tags
- /api/cart/          - Shopping cart
- /api/orders/        - Order management
- /api/payments/      - Payment operations
- /api/wishlist/      - User wishlists
- /api/reviews/       - Product reviews & ratings
- /api/delivery/      - Delivery addresses & shipping
- /api/analytics/     - Analytics & reporting (admin)
- /api/support/       - Customer support & tickets
- /api/reports/       - Business intelligence reports & exports (admin)

API Documentation:
- /api/docs/          - Swagger UI (drf-spectacular)
- /api/schema/        - OpenAPI 3.0 schema (JSON/YAML)
- /swagger/           - Legacy Swagger UI (drf-yasg)
- /redoc/             - ReDoc UI (drf-yasg)
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from apps.support.api_views import SocialLinksView, AppDownloadLinksView

# Legacy Swagger/OpenAPI documentation (drf-yasg)
schema_view = get_schema_view(
    openapi.Info(
        title="Modern E-Commerce API",
        default_version='v1',
        description="""
        Production-ready E-Commerce REST API
        
        Features:
        - Multi-gateway payment processing
        - JWT authentication
        - Order management
        - Product catalog
        - User wishlists & reviews
        - Delivery & shipping
        - Customer support
        """,
        terms_of_service="https://www.modernecommerce.com/terms/",
        contact=openapi.Contact(email="support@modernecommerce.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API endpoints (without version prefix for frontend compatibility)
    path('api/auth/', include('apps.auth.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/categories/', include('apps.categories.urls')),
    path('api/tags/', include('apps.tags.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/wishlist/', include('apps.wishlist.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
    path('api/delivery/', include('apps.delivery.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/support/', include('apps.support.urls')),
    path('api/help-support/', include('apps.support.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/social-links/', SocialLinksView.as_view(), name='social-links'),
    path('api/app-download-links/', AppDownloadLinksView.as_view(), name='app-download-links'),
    
    # API endpoints (with v1 prefix for backward compatibility)
    path('api/v1/auth/', include('apps.auth.urls')),
    path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/categories/', include('apps.categories.urls')),
    path('api/v1/tags/', include('apps.tags.urls')),
    path('api/v1/cart/', include('apps.cart.urls')),
    path('api/v1/wishlist/', include('apps.wishlist.urls')),
    path('api/v1/orders/', include('apps.orders.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/reviews/', include('apps.reviews.urls')),
    path('api/v1/delivery/', include('apps.delivery.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/support/', include('apps.support.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    
    # API Documentation - Modern (drf-spectacular)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Documentation - Legacy (drf-yasg) for backward compatibility
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui-legacy'),
    path('redoc-legacy/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-legacy'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
