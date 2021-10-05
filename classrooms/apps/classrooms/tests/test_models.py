"""
Tests for the `classroom` models module.
"""

from uuid import uuid4
from datetime import date
from unittest import mock

import ddt
from pytest import mark
from django.test import TestCase

from rest_framework import status

from classrooms.apps.classrooms.constants import DATE_FORMAT
from test_utils.factories import (
    ClassroomEnrollmentFactory,
    ClassroomFactory,
    CourseAssignmentFactory,
    UserFactory,
)
from test_utils.response import MockResponse


@mark.django_db
@ddt.ddt
class TestClassroomInstance(TestCase):
    """
    Tests for the Classroom model.
    """

    def setUp(self) -> None:

        self.name = "My Class"
        self.uuid = uuid4()
        self.classroom_instance = ClassroomFactory.create(
            name=self.name,
            school=self.uuid,
        )
        super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, method):
        """
        Test conversion to string
        """
        expected_str = (
            f"<ClassroomInstance {self.name} with ID {self.classroom_instance.uuid}>"
        )
        self.assertEqual(expected_str, method(self.classroom_instance))


@mark.django_db
@ddt.ddt
class TestClassroomEnrollment(TestCase):
    """
    Tests for the ClassroomEnrollment model.
    """

    def setUp(self) -> None:
        self.name = "My Class"
        self.uuid = uuid4()
        self.user = UserFactory.create()
        self.classroom_instance = ClassroomFactory.create(
            name=self.name,
            school=self.uuid,
        )
        self.classroom_enrollment = ClassroomEnrollmentFactory.create(
            classroom_instance=self.classroom_instance, user_id=self.user.id
        )
        return super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, method):
        """
        Test conversion to string
        """

        expected_str = f"<ClassroomEnrollment for user {self.user.id} in classroom with ID {self.classroom_instance.uuid}>"

        self.assertEqual(expected_str, method(self.classroom_enrollment))

    # TODO When classroom enrollment is created and course assignments exist, users should be enrolled


@mark.django_db
@ddt.ddt
class TestCourseAssignment(TestCase):
    """
    Tests for the Course
    """

    @mock.patch("classrooms.apps.api_client.base_oauth.OAuthAPIClient")
    def setUp(self, mock_oauth_client) -> None:

        self.classroom_instance = ClassroomFactory.create()
        self.template_course_id = "DiceyTech+BOX001+TEMPLATE"

        self.expected_course_run = (
            self.classroom_instance.name.replace(" ", "")
            + "_"
            + date.today().strftime(DATE_FORMAT)
        )

        self.expected_course_id = self.template_course_id.replace(
            "TEMPLATE", self.expected_course_run
        )

        mock_oauth_client.return_value.post.return_value = MockResponse(
            {"key": f"course-v1:{self.expected_course_id}"},
            status_code=status.HTTP_201_CREATED,
        )

        self.course_assignment = CourseAssignmentFactory.create(
            course_id=self.template_course_id,
            classroom_instance=self.classroom_instance,
        )

        super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, method):
        """
        Test conversion to string
        """

        expected_str = f"<CourseAssignment for course {self.course_assignment.course_id} in classroom with ID {self.classroom_instance.uuid}>"

        self.assertEqual(expected_str, method(self.course_assignment))

    def test_new_course_run_created(self):
        """
        Test that a new course run is created.
        """

        self.assertEqual(
            self.course_assignment.course_id,
            self.expected_course_id,
        )
