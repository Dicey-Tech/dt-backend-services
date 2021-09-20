"""
Discovery service api client code.
"""
import logging

from classrooms.apps.api_client.base_oauth import BaseOAuthClient
from classrooms.apps.api_client.constants import (
    DISCOVERY_COURSE_RUNS_ENDPOINT,
)


LOGGER = logging.getLogger(__name__)


class DiscoveryApiClient(BaseOAuthClient):
    """
    Object builds an API client to make calls to the Discovery Service.
    """

    def create_course_run(self, course_data):
        """ """

        try:
            LOGGER.info(f"Creating course run from course {course_data.get('course')}")

            response = self.client.post(
                DISCOVERY_COURSE_RUNS_ENDPOINT, params=course_data
            )

            return response
        except Exception as exc:
            LOGGER.exception(
                f"Could not create course run from course with key {course_data.get('course')}"
            )
            raise exc

    # TODO Get runs_type UUIDs
    # TODO get courses available
