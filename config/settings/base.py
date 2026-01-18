"""
Base Settings
-------------
Common settings shared across all environments.

This file contains settings that remain constant regardless of environment.
Environment-specific settings are in development.py, production.py, testing.py
"""
import os
from pathlib import Path
from datetime import timedelta

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'celery',
    'drf_yasg',
    'drf_spectacular',
    'django_filters',
    
    # Core app (must be before local apps for signal registration)
    'core.apps.CoreConfig',
    
    # Local apps (in apps/ directory)
    'apps.auth',
    'apps.products',
    'apps.cart',
    'apps.orders',
    'apps.payments',
    'apps.categories',
    'apps.promotions',
    "apps.tags",
    'apps.wishlist',
    'apps.reviews',
    'apps.delivery',
    'apps.analytics',
    'apps.support',
    'apps.reports',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.CacheControlMiddleware',  # Add cache control
    'core.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Authentication URLs
LOGIN_URL = '/api/auth/login/'
LOGIN_REDIRECT_URL = '/api/auth/profile/'
LOGOUT_REDIRECT_URL = '/api/auth/login/'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.environ.get('SECRET_KEY', 'insecure-key-for-development'),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Redis Cache Configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection.HiredisParser",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "IGNORE_EXCEPTIONS": True,  # Fail gracefully if Redis is down
        },
        "KEY_PREFIX": "ecommerce",
        "VERSION": 1,
        "TIMEOUT": 300,  # 5 minutes default
    }
}

# Cache timeout settings (in seconds)
CACHE_TTL = {
    'SHORT': 60 * 5,        # 5 minutes - frequently changing data
    'MEDIUM': 60 * 15,      # 15 minutes - semi-static data
    'LONG': 60 * 60,        # 1 hour - rarely changing data
    'DAY': 60 * 60 * 24,    # 24 hours - static data
}

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Email Configuration (override in environment-specific settings)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Payment Gateway Configuration
# These should be overridden by environment variables in production
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY', '')
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY', '')

FLUTTERWAVE_PUBLIC_KEY = os.environ.get('FLUTTERWAVE_PUBLIC_KEY', '')
FLUTTERWAVE_SECRET_KEY = os.environ.get('FLUTTERWAVE_SECRET_KEY', '')

# Security Settings (will be stricter in production)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# DRF Spectacular (OpenAPI 3.0) Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Modern E-Commerce API',
    'DESCRIPTION': '''
    Production-ready Django REST API for e-commerce platform.
    
    ## Features
    - 🔐 JWT Authentication (access & refresh tokens)
    - 🛍️ Complete product catalog with multi-image support
    - 🛒 Shopping cart & wishlist management
    - 📦 Order processing & tracking
    - 💳 Multi-gateway payment integration (Stripe, Paystack, Flutterwave, MoMo)
    - ⭐ Product reviews & ratings
    - 🚚 Delivery address management
    - 📊 Analytics & reporting (admin)
    - 💬 Customer support ticketing
    - 🎁 Promotions & discount management
    - 🏷️ Category & tag filtering
    - 🔍 Advanced search & filtering
    - ⚡ Redis caching for optimal performance
    
    ## Authentication
    Use JWT tokens in the Authorization header:
    ```
    Authorization: Bearer <your_access_token>
    ```
    
    Get tokens from `/api/auth/login/` endpoint.
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT': {
        'name': 'API Support',
        'email': 'support@modernecommerce.com'
    },
    'LICENSE': {
        'name': 'MIT License',
    },
    'TAGS': [
        {'name': 'Authentication', 'description': 'User registration, login, profile management'},
        {'name': 'Products', 'description': 'Product catalog, search, filtering'},
        {'name': 'Categories', 'description': 'Product categories and subcategories'},
        {'name': 'Cart', 'description': 'Shopping cart management'},
        {'name': 'Wishlist', 'description': 'User wishlist operations'},
        {'name': 'Orders', 'description': 'Order creation, tracking, history'},
        {'name': 'Payments', 'description': 'Payment processing, webhooks, refunds'},
        {'name': 'Reviews', 'description': 'Product reviews and ratings'},
        {'name': 'Delivery', 'description': 'Delivery addresses and shipping'},
        {'name': 'Analytics', 'description': 'Business analytics and insights (admin)'},
        {'name': 'Support', 'description': 'Customer support tickets'},
        {'name': 'Reports', 'description': 'Data export and reports (admin)'},
    ],
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
    },
    'PREPROCESSING_HOOKS': [],
    'POSTPROCESSING_HOOKS': [],
}

