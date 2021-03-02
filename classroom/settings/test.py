# -*- coding: utf-8 -*-
"""
These settings are here to use during tests, because django requires them.
In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "default.db",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}


SECRET_KEY = "insecure-secret-key"

LMS_INTERNAL_ROOT_URL = "http://localhost:8000"

OAUTH_ID_TOKEN_EXPIRATION = 60 * 60  # in seconds
