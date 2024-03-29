import os
from os.path import abspath, dirname, join

from corsheaders.defaults import default_headers as corsheaders_default_headers
from learninghub.apps.classrooms.constants import (
    CLASSROOM_LEARNER_ROLE,
    CLASSROOM_TEACHER_ROLE,
    SYSTEM_ENTERPRISE_ADMIN_ROLE,
    SYSTEM_ENTERPRISE_LEARNER_ROLE,
    SYSTEM_ENTERPRISE_OPERATOR_ROLE,
)
from learninghub.settings.utils import get_logger_config

# PATH vars
here = lambda *x: join(abspath(dirname(__file__)), *x)  # noqa E731
PROJECT_ROOT = here("..")
root = lambda *x: join(abspath(PROJECT_ROOT), *x)  # noqa E731


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("classroom_SECRET_KEY", "insecure-secret-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "release_util",
    "rules.apps.AutodiscoverRulesConfig",
)

THIRD_PARTY_APPS = (
    # API Documentation
    "drf_yasg",
    "edx_api_doc_tools",
    "corsheaders",
    "csrf.apps.CsrfAppConfig",  # Enables frontend apps to retrieve CSRF tokens
    "rest_framework",
    "social_django",
    "waffle",
)

PROJECT_APPS = (
    "learninghub.apps.core",
    "learninghub.apps.api",
    "learninghub.apps.classrooms",
)

INSTALLED_APPS += THIRD_PARTY_APPS
INSTALLED_APPS += PROJECT_APPS

MIDDLEWARE = (
    # Resets RequestCache utility for added safety.
    "edx_django_utils.cache.middleware.RequestCacheMiddleware",
    # Enables monitoring utility for writing custom metrics.
    "edx_django_utils.monitoring.CachedCustomMonitoringMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "edx_rest_framework_extensions.auth.jwt.middleware.JwtAuthCookieMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "waffle.middleware.WaffleMiddleware",
    # Enables force_django_cache_miss functionality for TieredCache.
    "edx_django_utils.cache.middleware.TieredCacheMiddleware",
    # Outputs monitoring metrics for a request.
    "edx_rest_framework_extensions.middleware.RequestCustomAttributesMiddleware",
    # Ensures proper DRF permissions in support of JWTs
    "edx_rest_framework_extensions.auth.jwt.middleware.EnsureJWTAuthSettingsMiddleware",
)

# Enable CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = corsheaders_default_headers + ("use-jwt-cookie",)
CORS_ORIGIN_WHITELIST = []

ROOT_URLCONF = "learninghub.urls"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "learninghub.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
# Set this value in the environment-specific files (e.g. local.py, production.py, test.py)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.",
        "NAME": "",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        "PORT": "",  # Set to empty string for default.
    }
}

# Django Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "edx_rest_framework_extensions.auth.jwt.authentication.JwtAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        "rest_framework.permissions.IsAdminUser",
    ],
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "PAGE_SIZE": 100,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (root("conf", "locale"),)


# MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = root("media")

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"
# END MEDIA CONFIGURATION


# STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = root("assets")

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (root("static"),)

# TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/2.2/ref/settings/#templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": (root("templates"),),
        "OPTIONS": {
            "context_processors": (
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "learninghub.apps.core.context_processors.core",
            ),
            "debug": True,  # Django will only display debug pages if the global DEBUG setting is set to True.
        },
    },
]
# END TEMPLATE CONFIGURATION


# COOKIE CONFIGURATION
# The purpose of customizing the cookie names is to avoid conflicts when
# multiple Django services are running behind the same hostname.
# Detailed information at: https://docs.djangoproject.com/en/dev/ref/settings/
SESSION_COOKIE_NAME = "classroom_sessionid"
CSRF_COOKIE_NAME = "classroom_csrftoken"
LANGUAGE_COOKIE_NAME = "classroom_language"
# END COOKIE CONFIGURATION

CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = []

# AUTHENTICATION CONFIGURATION
LOGIN_URL = "/login/"
LOGOUT_URL = "/logout/"

AUTH_USER_MODEL = "core.User"

AUTHENTICATION_BACKENDS = (
    "auth_backends.backends.EdXOAuth2",
    "rules.permissions.ObjectPermissionBackend",
    "django.contrib.auth.backends.ModelBackend",
)

ENABLE_AUTO_AUTH = False
AUTO_AUTH_USERNAME_PREFIX = "auto_auth_"

SOCIAL_AUTH_STRATEGY = "auth_backends.strategies.EdxDjangoStrategy"

# Set these to the correct values for your OAuth2 provider (e.g., LMS)
SOCIAL_AUTH_EDX_OAUTH2_KEY = "learninghub-sso-key"
SOCIAL_AUTH_EDX_OAUTH2_SECRET = "learninghub-sso-secret"
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = "http://127.0.0.1:8000"
SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL = "http://127.0.0.1:8000/logout"
BACKEND_SERVICE_EDX_OAUTH2_KEY = "learninghub-backend-service-key"
BACKEND_SERVICE_EDX_OAUTH2_SECRET = "learninghub-service-secret"

JWT_AUTH = {
    "JWT_ISSUER": "http://127.0.0.1:8000/oauth2",
    "JWT_ALGORITHM": "HS256",
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_PAYLOAD_GET_USERNAME_HANDLER": lambda d: d.get("preferred_username"),
    "JWT_LEEWAY": 1,
    "JWT_DECODE_HANDLER": "edx_rest_framework_extensions.auth.jwt.decoder.jwt_decode_handler",
    "JWT_PUBLIC_SIGNING_JWK_SET": None,
    "JWT_AUTH_COOKIE": "edx-jwt-cookie",
    "JWT_AUTH_COOKIE_HEADER_PAYLOAD": "edx-jwt-cookie-header-payload",
    "JWT_AUTH_COOKIE_SIGNATURE": "edx-jwt-cookie-signature",
    "JWT_AUTH_REFRESH_COOKIE": "edx-jwt-refresh-cookie",
    "JWT_SECRET_KEY": "SET-ME-PLEASE",
    # JWT_ISSUERS enables token decoding for multiple issuers (Note: This is not a native DRF-JWT field)
    # We use it to allow different values for the 'ISSUER' field, but keep the same SECRET_KEY and
    # AUDIENCE values across all issuers.
    "JWT_ISSUERS": [
        {
            "AUDIENCE": "SET-ME-PLEASE",
            "ISSUER": "http://localhost:18000/oauth2",
            "SECRET_KEY": "SET-ME-PLEASE",
        },
    ],
}

# Request the user's permissions in the ID token
EXTRA_SCOPE = ["permissions"]

# TODO Set this to another (non-staff, ideally) path.
LOGIN_REDIRECT_URL = "/admin/"
# END AUTHENTICATION CONFIGURATION


# OPENEDX-SPECIFIC CONFIGURATION
PLATFORM_NAME = "Your Platform Name Here"
# END OPENEDX-SPECIFIC CONFIGURATION

# Set up logging for development use (logging to stdout)
LOGGING = get_logger_config(debug=DEBUG)

# Default URLS for LMS
LMS_BASE_URL = os.environ.get("LMS_BASE_URL", "")

# Default URLs for CMS
CMS_BASE_URL = os.environ.get("CMS_BASE_URL", "")

# Set up system-to-feature roles mapping for edx-rbac
SYSTEM_TO_FEATURE_ROLE_MAPPING = {
    SYSTEM_ENTERPRISE_ADMIN_ROLE: [CLASSROOM_TEACHER_ROLE],
    SYSTEM_ENTERPRISE_OPERATOR_ROLE: [CLASSROOM_TEACHER_ROLE],
    SYSTEM_ENTERPRISE_LEARNER_ROLE: [CLASSROOM_LEARNER_ROLE],
}

# Default URLS for Discovery
DISCOVERY_SERVICE_API_URL = os.environ.get("DISCOVERY_SERVICE_API_URL", "")

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
