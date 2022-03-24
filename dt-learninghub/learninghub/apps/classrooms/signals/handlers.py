"""
Signal Handlers for users to be enrolled in courses.
"""
import logging
from typing import List

from django.db.models.signals import post_save
from django.dispatch import receiver
from learninghub.apps.api_client.enterprise import EnterpriseApiClient
from learninghub.apps.api_client.lms import LMSApiClient
from learninghub.apps.api_client.studio import StudioApiClient
from learninghub.apps.classrooms.models import ClassroomEnrollment, CourseAssignment

logger = logging.getLogger(__name__)


def enroll_learners(course_run_ids: List[str], identifiers: List[str]) -> None:
    """ """
    # client = LMSApiClient()
    client = EnterpriseApiClient()

    try:
        client.create_enterprise_enrollment(
            courses=course_run_ids, identifiers=identifiers
        )
        # client.bulk_enroll(courses=course_run_ids, identifiers=identifiers)
    except Exception as exc:
        logger.exception(f"Something went wrong... {exc}")


def enroll_staff(course_ids: List[str], identifiers: List[str]) -> None:
    """ """
    studio_client = StudioApiClient()
    lms_client = LMSApiClient()

    logger.info(
        f"Enroll {len(identifiers)} as instructor(s) in {len(course_ids)} courses."
    )

    try:
        for course in course_ids:
            course_data = {"team": []}

            usernames = lms_client.get_usernames(identifiers)

            course_data["team"] = [
                {"user": instructor, "role": "instructor"} for instructor in usernames
            ]

            studio_client.update_course_run(
                course_id=course, course_run_data=course_data
            )
    except Exception as exc:
        logger.exception(f"Something went wrong... {exc}")


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
        classroom_instance=instance.classroom_instance, staff=False
    )

    if not classroom_enrollments:
        return

    logger.info(
        f"Enroll {len(classroom_enrollments)} users in course with ID {instance.course_id}"
    )

    identifiers_list = [enrollment.user_id for enrollment in classroom_enrollments]

    course_run_id = [instance.course_id]

    enroll_learners(course_run_ids=course_run_id, identifiers=identifiers_list)

    staff_enrollments = classroom_enrollments.filter(staff=True)
    staff_list = [enrollment.user_id for enrollment in staff_enrollments]

    enroll_staff(course_ids=course_run_id, identifiers=staff_list)


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

    enroll_learners(course_run_ids=course_ids_list, identifiers=[instance.user_id])

    is_staff = ClassroomEnrollment.objects.filter(
        classroom_instance=instance.classroom_instance,
        user_id=instance.user_id,
    )[0].staff

    if is_staff:
        enroll_staff(course_ids=course_ids_list, identifiers=[instance.user_id])
