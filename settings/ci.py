import os
from django_jenkins.settings import *  # or from .settings import * if you use a single-file layout

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "ci-not-for-prod")
DEBUG = True
ALLOWED_HOSTS = ["*"]

# Oracle DB settings: Jenkins will provide env vars
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.oracle",
        # Django will assemble a DSN from these three:
        "NAME": os.environ.get("ORA_SERVICE", "ORA_SERVICE"),  # service name
        "HOST": os.environ.get("ORA_HOST", "ORA_HOST"),
        "PORT": os.environ.get("ORA_PORT", "ORA_PORT"),
        "USER": os.environ.get("ORA_USER", "ORA_USER"),
        "PASSWORD": os.environ.get("ORA_PASSWORD", "ORA_PASSWORD"),
        "OPTIONS": {
            # Optional, but keeps encodings sane
            "encoding": "UTF-8",
            "nencoding": "UTF-8",
        },
    }
}

# Keep migrations sane in CI (optional)
MIGRATION_MODULES = {
    # e.g., "app_that_has_huge_migrations": None
}

# Fast password hasher for tests (optional)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # One year in seconds (example)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SILENCED_SYSTEM_CHECKS = [
    'security.W009',  # Example: Silences the SECURE_HSTS_SECONDS warning
    'security.W018',  # Another example
]
