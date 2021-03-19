"""
classroom Django application initialization.
"""

from django.apps import AppConfig
from edx_django_utils.plugins.constants import (
    PluginURLs,
    PluginSettings,
    PluginContexts,
)

# TODO https://github.com/edx/edx-django-utils/blob/master/edx_django_utils/plugins/README.rst#id4
class ClassroomConfig(AppConfig):
    """
    Configuration for the classroom Django application.
    """

    name = "classroom"
