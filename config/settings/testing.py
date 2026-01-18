"""
Testing Settings
----------------
Settings for running automated tests.

Characteristics:
- Fast in-memory database
- No email sending
- Simplified middleware
- Faster password hashing
"""
from .base import *

# Use in-memory SQLite for speed
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests (use --nomigrations flag)
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

# MIGRATION_MODULES = DisableMigrations()

# Fast password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging in tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# Email - Memory backend
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Celery - Synchronous for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Debug
DEBUG = False

# Secret key for tests
SECRET_KEY = 'test-secret-key-not-for-production'

# Allowed hosts
ALLOWED_HOSTS = ['*']
