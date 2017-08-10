"""
Development settings using sqlite3 and DEBUG = TRUE
"""
import os
# Load defaults in order to then add/override with dev-only settings
from .defaults import *

DEBUG = True
TEMPLATES[0]['TEMPLATE_DEBUG'] = DEBUG

DATACITE_REST_URL='https://mds.test.datacite.org/'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
