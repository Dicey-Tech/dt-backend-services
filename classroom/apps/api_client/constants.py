"""
Constants for each API Client.
"""
from urllib.parse import urljoin

from django.conf import settings

# Enterprise API Client Constants
ENTERPRISE_API_URL = urljoin(settings.LMS_BASE_URL, "/enterprise/api/v1/")
ENTERPRISE_CUSTOMER_ENDPOINT = urljoin(ENTERPRISE_API_URL, "enterprise-customer/")
ENTERPRISE_LEARNER_ENDPOINT = urljoin(ENTERPRISE_API_URL, "enterprise-learner/")
ENTERPRISE_CUSTOMER_CACHE_KEY_TPL = "customer:{uuid}"
