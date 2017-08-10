"""
Production settings
"""
# Load defaults in order to then add/override with dev-only settings
from .defaults import *
import os

DATACITE_REST_URL='https://mds.datacite.org/'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

EMAIL_HOST = os.environ["EMAIL_HOST"]
EMAIL_PORT = os.environ.get("EMAIL_PORT",25)
EMAIL_HOST_USER = os.environ["EMAIL_USER"]
