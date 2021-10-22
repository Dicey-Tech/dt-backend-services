""" Abstraction layer to handle the implementation details for course runs """
# from datetime import datetime, timedelta
from typing import Dict, Any
import logging

from classrooms.apps.api_client.discovery import DiscoveryApiClient
from classrooms.apps.api_client.studio import StudioApiClient

logger = logging.getLogger(__name__)

# TODO Add tests
def create_course_run(
    template_course_id: str, course_data: Dict[str, str]
) -> Dict[str, Any]:
    """Create a course run"""
    client = DiscoveryApiClient()

    # First we need to get the UUID of the run type
    # associated with the course that we use as template
    run_type = client.get_course_run_type(template_course_id)

    course_data["run_type"] = run_type

    # Create the course a course rerun from the template
    response = client.create_course_run(course_data)

    # When creating a course rerun, the dates are not published
    # A staff member would have to update the Schedule from studio
    # to get the dates published.
    # This is a workaround to force publish the dates by updating the
    # schedule using the studio API.
    _publish_course_run_dates(response)

    return response.get("key")


def _publish_course_run_dates(course_run_data: Dict[str, Any]) -> None:
    """Make a call to update a course run dates"""

    client = StudioApiClient()

    schedule = {
        "schedule": {
            "start": course_run_data["start"],
            "end": course_run_data["end"],
        }
    }

    client.update_course_run(course_id=course_run_data["key"], course_run_data=schedule)
