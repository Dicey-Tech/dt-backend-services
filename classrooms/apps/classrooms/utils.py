"""  """
# from datetime import datetime, timedelta
from classrooms.apps.api_client.discovery import DiscoveryApiClient


def get_course_list():
    """Return a list of template courses"""
    client = DiscoveryApiClient()

    return client.get_course_list()
