""" Abstraction layer to handle the implementation details for listing available courses """
import logging
from typing import List

from learninghub.apps.api_client.enterprise import EnterpriseApiClient
from learninghub.apps.classrooms.models import CourseAssignment
from opaque_keys.edx.keys import CourseKey

logger = logging.getLogger(__name__)


# TODO Add tests
def get_course_list(classroom_uuid: str) -> List:
    """Return a list of template courses"""
    client = EnterpriseApiClient()

    return _filter_course_list(classroom_uuid, client.get_course_list())


def _filter_course_list(classroom_uuid: str, course_list: List) -> List:
    """Filter out the courses that are already assigned"""
    logger.debug(f"Filter course list with {len(course_list)} courses")

    assignments = CourseAssignment.objects.filter(
        classroom_instance__uuid=classroom_uuid
    )

    logger.debug(f"In classroom with {len(assignments)} assignments")

    for assignment in assignments:
        existing_assignment_key = CourseKey.from_string(assignment.course_id)

        for listed_course in course_list:
            key = CourseKey.from_string(listed_course["key"])

            if key.course == existing_assignment_key.course:
                course_list.remove(listed_course)

        if len(course_list) == 0:
            break

    logger.debug(f"Filtered list has {len(course_list)} course(s)")
    return course_list
