"""  """
import logging
from urllib.parse import urljoin

import requests
from classrooms.apps.api_client.base_oauth import BaseOAuthClient
from classrooms.apps.api_client.constants import (
    ENTERPRISE_CUSTOMER_ENDPOINT,
    ENTERPRISE_LEARNER_ENDPOINT,
    ENTERPRISE_COURSE_ENROLLMENT,
)

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

        response = self.client.get(
            ENTERPRISE_CUSTOMER_ENDPOINT, params=query_params
        ).json()

        results = response.get("results", [])
        enterprise_customer = results[0] if results else {}

        return enterprise_customer

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

    def create_enterprise_enrollment(self, school_uuid, user_id, course_id):
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

        enrollment_data = [
            {
                "course_mode": "honor",
                "course_run_id": course_id,
                "lms_user_id": user_id,
                "email_students": False,
            }
        ]

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
        except requests.exceptions.HTTPError as exc:
            logger.error(
                f"Failed to create EnterpriseCourseEnrollment record for school {school_uuid} because {response.text}"
            )
            raise exc

    def create_enterprise_enrollment_record():
        """
        #TODO This is temporary. Because create_enterprise_enrollment requires the enterprise-catalog
        service, we're using this call to create a record of an enterprise enrollment and a separate
        LmsApiClient to actually enroll users.


        /enterprise /api/v1/enterprise-course-enrollment/
        {
            "username": "sofiane",
            "course_id": "course-v1:DiceyTech+DT002+3T2021b"
        }
        """

        pass
