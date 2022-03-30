"""
Tests for the `classroom` models module.
"""

from datetime import date
from unittest import mock
from uuid import uuid4

import ddt
from django.test import TestCase
from learninghub.apps.classrooms.constants import DATE_FORMAT
from pytest import mark
from rest_framework import status
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
            classroom_instance=self.classroom_instance, lms_user_id=self.user.id
        )
        return super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, method):
        """
        Test conversion to string
        """

        expected_str = f"<ClassroomEnrollment for user {self.user.id} in classroom with ID {self.classroom_instance.uuid}>"

        self.assertEqual(expected_str, method(self.classroom_enrollment))


@mark.django_db
@ddt.ddt
class TestCourseAssignment(TestCase):
    """
    Tests for the Course
    """

    @mock.patch("learninghub.apps.api_client.base_oauth.OAuthAPIClient")
    def setUp(self, mock_oauth_client) -> None:

        self.classroom_instance = ClassroomFactory.create()
        self.template_course_id = "course-v1:DiceyTech+BOX001+TEMPLATE"

        self.expected_course_run = (
            self.classroom_instance.name.replace(" ", "")
            + "_"
            + date.today().strftime(DATE_FORMAT)
        )

        self.expected_course_id = self.template_course_id.replace(
            "TEMPLATE", self.expected_course_run
        )

        mock_oauth_client.return_value.post.return_value = MockResponse(
            {
                "key": self.expected_course_id,
                "start": "2021-09-18T14:40:00Z",
                "end": "2021-12-18T14:40:00Z",
            },
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
