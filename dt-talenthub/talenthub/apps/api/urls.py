"""
Root API URLs.

All API URLs should be versioned, so urlpatterns should only
contain namespaces for the active versions of the API.
"""
from django.conf.urls import include
from django.urls import re_path
from talenthub.apps.api.v1 import urls as v1_urls

app_name = "api"
urlpatterns = [
    re_path(r"^v1/", include(v1_urls)),
]
