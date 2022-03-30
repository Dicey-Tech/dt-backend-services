"""
LMS service api client code.
"""

import logging
from typing import Dict, List

from learninghub.apps.api_client.base_oauth import BaseOAuthClient
from learninghub.apps.api_client.constants import (
    LMS_BULK_ENROLLMENT_ENDPOINT,
    LMS_USER_ENDPOINT,
)
from requests.exceptions import HTTPError

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

        try:
            logger.info(
                f"Enroll {len(identifiers.split(','))} learner(s) in {len(courses.split(','))} course(s)"
            )

            response = self.client.post(LMS_BULK_ENROLLMENT_ENDPOINT, json=data)

            response.raise_for_status()

            return response
        except HTTPError as exc:
            logger.error(f"Bulk enroll failed {exc}")

            return

    def get_usernames(self, emails_list: List[str]) -> List[str]:
        """Given a list of user emails, return a list of ursernames"""
        usernames = []

        for email in emails_list:
            response = self.get_user_details(email=email)
            if not response:
                return []

            usernames.append(response.get("username"))

        return usernames

    def get_user_details(
        self, email=None, user_id=None, username=None
    ) -> Dict[str, str]:
        """Get user details"""

        if not any((email, user_id, username)):
            return

        query_params = ""

        if email:
            query_params = f"email={email}"
        elif user_id:
            query_params = f"lms_user_id={user_id}"
        elif username:
            query_params = f"username={username}"

        try:
            response = self.client.get(LMS_USER_ENDPOINT, params=query_params)

            response.raise_for_status()

            return response.json()[0]
        except HTTPError as exc:
            logger.error(f"Could not get user details {exc}")

            return {}

    def remove_discovery_user(self, course):
        """Remove discovery user from learner list in course"""

        data = {
            "auto_enroll": True,
            "email_students": "no",
            "action": "unenroll",
            "courses": course,
            "identifiers": "discovery",
        }

        try:
            response = self.client.post(LMS_BULK_ENROLLMENT_ENDPOINT, json=data)

            response.raise_for_status()

            return response
        except HTTPError as exc:
            logger.error(f"Failed to remove discovery user {exc}")

            return
