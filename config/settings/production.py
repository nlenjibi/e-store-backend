"""
Production Settings
-------------------
Settings for production deployment on Railway.

Characteristics:
- DEBUG = False
- PostgreSQL database
- Strict security
- HTTPS enforced
- Real email backend
- Error logging
- Performance optimizations
"""
from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# SECURITY CRITICAL
DEBUG = False

# MUST be set via environment variable
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set in production")

# Railway automatically provides the app URL, but allow custom domains
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'e-store-backend-production.up.railway.app').split(',')
# Add Railway's default domain
ALLOWED_HOSTS.append('.railway.app')
ALLOWED_HOSTS.append('.up.railway.app')

# Get PORT from Railway environment
PORT = int(os.environ.get('PORT', 8000))

# Database - PostgreSQL for production (Railway format)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PGDATABASE', os.getenv('NAME')),
        'USER': os.getenv('PGUSER', os.getenv('DB_USER')),
        'PASSWORD': os.getenv('PGPASSWORD', os.getenv('DB_PASSWORD')),
        'HOST': os.getenv('PGHOST', os.getenv('DB_HOST')),
        'PORT': os.getenv('PGPORT', os.getenv('DB_PORT', '5432')),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CORS - Allow Railway domains and custom domains
CORS_ALLOWED_ORIGINS = [
    'https://e-store-backend-production.up.railway.app',
]
# Add additional origins from environment variable
additional_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
if additional_origins:
    CORS_ALLOWED_ORIGINS.extend(additional_origins.split(','))

CORS_ALLOW_CREDENTIALS = True

# Trusted origins for CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://e-store-backend-production.up.railway.app',
    'https://*.railway.app',
    'https://*.up.railway.app',
]
# Add additional trusted origins from environment variable
additional_trusted = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if additional_trusted:
    CSRF_TRUSTED_ORIGINS.extend(additional_trusted.split(','))

# Email Configuration - Real SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@example.com')

# Logging - Send errors to file and external service
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# Sentry Error Tracking (optional - configure if using Sentry)
SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

# Static files - Use WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Redis Cache - Railway format or custom
REDIS_URL = os.environ.get('REDIS_URL')
if not REDIS_URL:
    # Build from individual components if REDIS_URL not provided
    redis_password = os.environ.get('REDIS_PASSWORD', os.environ.get('REDISPASSWORD'))
    redis_host = os.environ.get('REDIS_HOST', os.environ.get('REDISHOST'))
    redis_port = os.environ.get('REDIS_PORT', os.environ.get('REDISPORT', '6379'))
    
    if redis_password and redis_host:
        REDIS_URL = f'redis://:{redis_password}@{redis_host}:{redis_port}/1'
    else:
        REDIS_URL = 'redis://localhost:6379/1'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'IGNORE_EXCEPTIONS': True,
        }
    }
}

# Celery - Use Redis as broker
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
if not CELERY_BROKER_URL:
    redis_password = os.environ.get('REDIS_PASSWORD', os.environ.get('REDISPASSWORD'))
    redis_host = os.environ.get('REDIS_HOST', os.environ.get('REDISHOST'))
    redis_port = os.environ.get('REDIS_PORT', os.environ.get('REDISPORT', '6379'))
    
    if redis_password and redis_host:
        CELERY_BROKER_URL = f'redis://:{redis_password}@{redis_host}:{redis_port}/0'
    else:
        CELERY_BROKER_URL = 'redis://localhost:6379/0'

CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Session - Use cache backend
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'