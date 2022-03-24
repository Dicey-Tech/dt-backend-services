"""
Constants for each API Client.
"""
from urllib.parse import urljoin

from django.conf import settings

# LMS API Client Constants
LMS_BULK_ENROLLMENT_ENDPOINT = urljoin(
    settings.LMS_BASE_URL, "/api/bulk_enroll/v1/bulk_enroll"
)
LMS_USER_ENDPOINT = urljoin(settings.LMS_BASE_URL, "/api/user/v1/accounts")

# Studio API Client Constants
STUDIO_COURSE_RUNS_ENDPOINT = urljoin(settings.CMS_BASE_URL, "api/v1/course_runs/")

# Discovery API Client Constants
DISCOVERY_SEARCH_ALL_ENDPOINT = urljoin(
    settings.DISCOVERY_SERVICE_API_URL, "search/all/"
)
DISCOVERY_COURSE_RUNS_ENDPOINT = urljoin(
    settings.DISCOVERY_SERVICE_API_URL, "course_runs/"
)
DISCOVERY_COURSES_ENDPOINT = urljoin(settings.DISCOVERY_SERVICE_API_URL, "courses/")
DISCOVERY_CATALOGS_ENDPOINT = urljoin(settings.DISCOVERY_SERVICE_API_URL, "catalogs/")
DISCOVERY_OFFSET_SIZE = 200
DISCOVERY_CATALOG_QUERY_CACHE_KEY_TPL = "catalog_query:{id}"

# Enterprise API Client Constants
ENTERPRISE_API_URL = urljoin(settings.LMS_BASE_URL, "/enterprise/api/v1/")
ENTERPRISE_CATALOG_ENDPOINT = urljoin(ENTERPRISE_API_URL, "enterprise_catalogs/")
ENTERPRISE_CUSTOMER_ENDPOINT = urljoin(ENTERPRISE_API_URL, "enterprise-customer/")
ENTERPRISE_LEARNER_ENDPOINT = urljoin(ENTERPRISE_API_URL, "enterprise-learner/")
ENTERPRISE_COURSE_ENROLLMENT = urljoin(
    ENTERPRISE_API_URL, "enterprise-course-enrollment/"
)
ENTERPRISE_CUSTOMER_CACHE_KEY_TPL = "customer:{uuid}"
