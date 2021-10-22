"""
LMS service api client code.
"""

import logging
from typing import List

from classrooms.apps.api_client.base_oauth import BaseOAuthClient
from classrooms.apps.api_client.constants import (
    LMS_BULK_ENROLLMENT_ENDPOINT,
    LMS_USER_ENDPOINT,
)

logger = logging.getLogger(__name__)


class LMSApiClient(BaseOAuthClient):
    """
    Object builds an API client to make calls to the LMS Service.
    """

    def bulk_enroll(
        self, courses: List[str], identifiers: List[str], email_students: bool = False
    ) -> None:
        """
        Enroll a list of students in a list of courses.

        TODO Since the Enterprise enrollment endpoint requires the enterprise-catalog
        service, we will use this endpoint until I know how to set it up.
        """

        courses = ",".join(courses)
        identifiers = ",".join(identifiers)

        data = {
            "auto_enroll": True,
            "email_students": email_students,
            "action": "enroll",
            "courses": courses,
            "identifiers": identifiers,
        }

        logger.debug(data)

        try:
            logger.info(
                f"Enroll {len(identifiers.split(','))} learner(s) in {len(courses.split(','))} course(s)"
            )

            response = self.client.post(LMS_BULK_ENROLLMENT_ENDPOINT, json=data)

            response.raise_for_status()

            return response
        except Exception as exc:
            logger.exception(f"Something went wrong {exc}")  # TODO Better message

            raise exc

    def get_usernames(self, emails_list: List[str]) -> List[str]:
        """Given a list of user emails, return a list of ursernames"""
        usernames = []

        try:
            for email in emails_list:
                query_param = "email=" + email
                response = self.client.get(LMS_USER_ENDPOINT, params=query_param)

                response.raise_for_status()

                usernames.append(response.json()[0]["username"])

            logger.debug(usernames)

            return usernames
        except Exception as exc:
            logger.exception(f"Something went wrong {exc}")  # TODO Better message

            raise exc
