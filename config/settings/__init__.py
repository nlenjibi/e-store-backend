"""
Settings Module
---------------
Automatically loads the correct settings file based on DJANGO_SETTINGS_MODULE.

Default: development settings
Production: Set DJANGO_SETTINGS_MODULE=config.settings.production
Testing: Set DJANGO_SETTINGS_MODULE=config.settings.testing
"""
import os

# Determine which settings to use
ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'testing':
    from .testing import *
else:
    from .development import *
