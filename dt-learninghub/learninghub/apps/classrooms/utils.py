""" Utility functions for classrooms app. """

from learninghub.apps.api_client.lms import LMSApiClient


def get_lms_user_id(email: str) -> int:
    lms_client = LMSApiClient()

    details = lms_client.get_user_details(email=email)

    return details.get("id")
