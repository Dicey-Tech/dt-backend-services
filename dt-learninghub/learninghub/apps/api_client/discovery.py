"""
Discovery service api client code.
"""
import logging

from learninghub.apps.api_client.base_oauth import BaseOAuthClient
from learninghub.apps.api_client.constants import (
    DISCOVERY_CATALOGS_ENDPOINT,
    DISCOVERY_COURSE_RUNS_ENDPOINT,
)
from opaque_keys.edx.keys import CourseKey
from requests.exceptions import HTTPError

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

            logger.info(f"Created course run {response.json().get('key')}")
            return response.json()
        except HTTPError as exc:
            logger.exception(
                f"Could not create course run from course with data {course_data}"
            )
            raise exc

    def get_course_run_type(self, course_key: CourseKey):
        """Get Run Type UUID from Course"""

        try:
            logger.info(f"Get run type UUID from course {course_key}")

            response = self.client.get(
                DISCOVERY_COURSE_RUNS_ENDPOINT, params={"keys": course_key}
            )
            response.raise_for_status()

            logger.debug(response.json())
            if not response.json().get("results"):
                return ""

            run_type = response.json().get("results")[0].get("run_type")

            return run_type
        except IndexError as exc:  # noqa F841
            logger.error(f"No run type was found for {course_key}")

            return None
        except HTTPError as exc:
            logger.error(
                f"Could not get course details for course run with key {course_key}"
            )
            raise exc

    # TODO get courses available for school/teacher
    def get_course_list(self):
        """Return a list of courses to use as templates for course assignments"""
        try:
            catalog_names = ["Starter Pack", "Creator Pack", "Maker Pack"]
            logger.info(f"Get course list for catalogs {str(catalog_names)}")

            response = self.client.get(DISCOVERY_CATALOGS_ENDPOINT).json()

            logger.info(f"Response: {response}")
            catalogs_ids = []

            for catalog in response.get("results"):
                if catalog["name"] in catalog_names and catalog["courses_count"] > 0:
                    catalogs_ids.append(catalog["id"])

            course_list = []

            for id in catalogs_ids:
                response = self.client.get(
                    DISCOVERY_CATALOGS_ENDPOINT + f"{id}/courses"
                ).json()

                for course in response.get("results"):
                    for course_run in course["course_runs"]:
                        if "TEMPLATE" in course_run["key"]:
                            course_list.append(course_run)

            logger.debug(f"Found {len(course_list)} courses.")

            return course_list

        except HTTPError as exc:
            logger.error(f"Could not retrieve course list because of{exc}")

            return []
