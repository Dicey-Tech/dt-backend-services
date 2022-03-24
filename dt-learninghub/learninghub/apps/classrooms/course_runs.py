""" Abstraction layer to handle the implementation details for course runs """
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from learninghub.apps.api_client.discovery import DiscoveryApiClient
from learninghub.apps.api_client.lms import LMSApiClient
from learninghub.apps.api_client.studio import StudioApiClient
from learninghub.apps.classrooms.constants import COURSE_RUN_FORMAT, DATETIME_FORMAT
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

logger = logging.getLogger(__name__)


def _calculate_course_run_key_run_value(create_at: datetime) -> str:
    """Generate a Course Run Key"""
    # Simple implementation for now
    return create_at.strftime(COURSE_RUN_FORMAT)


# TODO Add tests
def create_course_run(template_course_id: str) -> str:
    """Create a course run"""

    start = datetime.today()
    end = start + timedelta(days=90)

    run = _calculate_course_run_key_run_value(start)

    try:
        course = CourseKey.from_string(template_course_id)
        # If the course is not a template then link it directly to the classroom
        if course.run != "TEMPLATE":
            return template_course_id
    except InvalidKeyError:
        logger.error(f"Course key {template_course_id} is not recognised.")

    course_data = {
        "start": start.strftime(DATETIME_FORMAT),
        "end": end.strftime(DATETIME_FORMAT),
        "pacing_type": "self_paced",
        "run_type": "",
        "status": "published",
        "course": f"{course.org}+{course.course}",
        "term": run,
    }

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

    # Remove discovery learner
    lms_client = LMSApiClient()
    lms_client.remove_discovery_user(response.get("key"))

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
