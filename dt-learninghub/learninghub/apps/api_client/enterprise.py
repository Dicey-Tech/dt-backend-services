"""  """
import logging
from typing import List
from urllib.parse import urljoin

from learninghub.apps.api_client.base_oauth import BaseOAuthClient
from learninghub.apps.api_client.constants import (
    ENTERPRISE_CATALOG_ENDPOINT,
    ENTERPRISE_CUSTOMER_ENDPOINT,
    ENTERPRISE_LEARNER_ENDPOINT,
)
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)


class EnterpriseApiClient(BaseOAuthClient):
    """
    API client for calls to the enterprise service.
    """

    def get_enterprise_customer(self, customer_uuid):
        """
        Retrieve an Enterprise Customer record from the edx-enterprise API.

        Arguments:
            customer_uuid: string representation of the customer's uuid

        Returns:
            enterprise_customer: dictionary record for customer with given uuid or
                                 empty dictionary if no customer record found
        """
        query_params = {"uuid": customer_uuid}
        try:
            response = self.client.get(
                ENTERPRISE_CUSTOMER_ENDPOINT, params=query_params
            ).json()

            results = response.get("results", [])
            enterprise_customer = results[0] if results else {}

            return enterprise_customer
        except HTTPError as exc:
            logger.error(
                f"Could not retrieve details for Enterprise Customer <{customer_uuid}> because of{exc}"
            )

            return {}

    def get_enterprise_learners(self, customer_uuid):
        """
        Retrieve Enterprise Learner(s) record(s) from the edx-enterprise API.

        Arguments:
            customer_uuid: string representation of the customer's uuid

        Returns:
            enterprise_learner: dictionary record for learners with given uuid or
                                 empty dictionary if no learner record found
        """
        query_params = {"uuid": customer_uuid}

        response = self.client.get(
            ENTERPRISE_LEARNER_ENDPOINT, params=query_params
        ).json()

        results = response.get("results", [])
        learners_data = results if results else {}

        return learners_data

    def create_enterprise_enrollment(
        self, courses: List[str], identifiers: List[str], school_uuid: str
    ):
        """

        Requires the enterprise-catalog service.

        Arguments:
            school_uuid:
            user_id:
            course_id":
        Returns:

        enterprise/api/v1/enterprise-customer/<UUID>/course_enrollments
        [{
            'course_mode': "honor",
            'course_run_id': 'course-v1:edX+DemoX+Demo_Course',
            'lms_user_id': 10,
        }]
        """
        enrollment_data = []
        for course_id in courses:
            for user_id in identifiers:
                enrollment_data.append(
                    {
                        "course_mode": "honor",
                        "course_run_id": course_id,
                        "lms_user_id": user_id,
                        "email_students": True,
                        "is_active": True,
                    }
                )

        logger.debug(f"{enrollment_data}")
        response = self.client.post(
            f"{ENTERPRISE_CUSTOMER_ENDPOINT}{school_uuid}/course_enrollments/",
            json=enrollment_data,
        )

        try:
            response.raise_for_status()

            logger.info(
                f"Successfully created EnterpriseCourseEnrollment record for school {school_uuid}."
            )

            return response
        except HTTPError as exc:
            logger.error(
                f"Failed to create EnterpriseCourseEnrollment record for school {school_uuid} because {response.text}"
            )
            raise exc

    def get_course_list(self, customer_uuid):
        """
        Fetch the list of template courses accessible to the enterprise user

        Arguments:
            customer_uuid: string representation of the enterprise customer's uuid

        Returns:
            course_list:
        """
        course_list = []

        try:
            catalog_list = self.get_enterprise_customer(customer_uuid).get(
                "enterprise_customer_catalogs", []
            )

            for catalog in catalog_list:
                endpoint = urljoin(ENTERPRISE_CATALOG_ENDPOINT, f"{catalog}/")
                response = self.client.get(endpoint).json()
                courses = response.get("results", [])

                for course in courses:
                    if course.get("key"):
                        # This is to maintain the compatibilty with the way the discovery
                        # API client would return a list of courses
                        course_list.append(
                            {
                                "key": course.get("key"),
                                "uuid": None,  # Not used in frontend
                                "title": course.get("title"),
                                "image": {
                                    "src": course.get("image_url"),
                                },
                                "short_description": course.get("short_description"),
                            }
                        )

            return course_list
        except HTTPError as exc:
            logger.error(f"Could not retrieve course list because of{exc}")

            return []
