"""
Discovery service api client code.
"""
import logging
import json

from classrooms.apps.api_client.base_oauth import BaseOAuthClient
from classrooms.apps.api_client.constants import (
    DISCOVERY_COURSE_RUNS_ENDPOINT,
)


logger = logging.getLogger(__name__)


class DiscoveryApiClient(BaseOAuthClient):
    """
    Object builds an API client to make calls to the Discovery Service.
    """

    def create_course_run(self, course_data):
        """Create a new course run for the specified course"""

        try:
            logger.info(f"Creating course run from course {course_data.get('course')}")

            response = self.client.post(
                DISCOVERY_COURSE_RUNS_ENDPOINT, json=course_data
            )

            response.raise_for_status()

            return response
        except Exception as exc:
            logger.exception(
                f"Could not create course run from course with key {course_data.get('course')}"
            )
            raise exc

    # TODO Get runs_type UUIDs http://discovery.local.overhang.io/api/v1/courses/DiceyTech%2BEXP001/
    def get_course_run_type(self, course_key):
        """Get Run Type UUID from Course"""
        course_key = "course-v1:" + course_key

        try:
            logger.info(f"Get run type UUID from course {course_key}")

            response = self.client.get(
                DISCOVERY_COURSE_RUNS_ENDPOINT, params={"keys": course_key}
            )

            run_type = response.json().get("results")[0].get("run_type")

            return run_type
        except Exception as exc:
            logger.exception(
                f"Could not get course details for course run with key {course_key}"
            )
            raise exc

    # TODO get courses available for school/teacher
