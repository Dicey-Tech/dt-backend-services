"""
LMS service api client code.
"""

import logging

from classrooms.apps.api_client.base_oauth import BaseOAuthClient
from classrooms.apps.api_client.constants import LMS_BULK_ENROLLMENT_ENDPOINT

logger = logging.getLogger(__name__)


class LMSApiClient(BaseOAuthClient):
    """
    Object builds an API client to make calls to the LMS Service.
    """

    def bulk_enroll(self, courses, usernames, email_students=False):
        """
        Enroll a list of students in a list of courses.

        TODO Since the Enterprise enrollment endpoint requires the enterprise-catalog
        service, we will use this endpoint until I know how to set it up.
        """
        data = {
            "auto_enroll": True,
            "email_students": email_students,
            "action": "enroll",
            "courses": courses,
            "identifiers": usernames,
        }

        logger.debug(data)

        try:
            logger.info(
                f"Enroll {len(usernames.split(','))} learner(s) in {len(courses.split(','))} course(s)"
            )

            response = self.client.post(LMS_BULK_ENROLLMENT_ENDPOINT, json=data)

            response.raise_for_status()

            return response
        except Exception as exc:
            logger.exception(f"Something went wrong {exc}")  # TODO Better message

            raise exc
