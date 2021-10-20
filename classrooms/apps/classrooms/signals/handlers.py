""" 
Signal Handlers for users to be enrolled in courses.
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from classrooms.apps.classrooms.models import CourseAssignment, ClassroomEnrollment
from classrooms.apps.api_client.lms import LMSApiClient

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CourseAssignment)
def enroll_from_course_assignment(sender, instance, created, **kwargs):
    """
    When a CourseAssignment is created, which includes the classroom specific
    course run, lookup all existing ClassroomEnrollments. For each student, enroll them
    in the newly create course run.
    """

    if not created:
        return

    classroom_enrollments = ClassroomEnrollment.objects.filter(
        classroom_instance=instance.classroom_instance
    )

    if not classroom_enrollments:
        return

    logger.info(
        f"Enroll {len(classroom_enrollments)} users in course with ID {instance.course_id}"
    )

    identifiers_list = [enrollment.user_id for enrollment in classroom_enrollments]
    identifiers = ",".join(identifiers_list)

    course_run_id = instance.course_id

    client = LMSApiClient()

    try:
        client.bulk_enroll(courses=course_run_id, usernames=identifiers)
    except Exception as exc:
        logger.exception(f"Something went wrong... {exc}")


@receiver(post_save, sender=ClassroomEnrollment)
def enroll_from_classroom_enrollment(sender, instance, created, **kwargs):
    """
    When a ClassroomEnrollment is created, lookup all existing CourseAssignments. For each
    assignment, enroll the students in the course.
    """
    if not created:
        return

    course_assignments = CourseAssignment.objects.filter(
        classroom_instance=instance.classroom_instance
    )

    if not course_assignments:
        return

    logger.info(f"Enroll user {instance.user_id} in {len(course_assignments)} courses")

    course_ids_list = [course.course_id for course in course_assignments]
    courses = ",".join(course_ids_list)

    client = LMSApiClient()

    try:
        client.bulk_enroll(courses=courses, usernames=instance.user_id)
    except Exception as exc:
        logger.exception(f"Something went wrong {exc}")
