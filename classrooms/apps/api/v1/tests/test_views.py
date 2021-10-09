"""
Classroom API Test Cases
"""

import logging
import json
from uuid import uuid4
from datetime import date
from unittest import mock

import ddt
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from edx_rest_framework_extensions.auth.jwt.cookies import jwt_cookie_name
from edx_rest_framework_extensions.auth.jwt.tests.utils import (
    generate_jwt_token,
    generate_unversioned_payload,
)

from classrooms.apps.classrooms import constants
from test_utils.factories import (
    CourseAssignmentFactory,
    UserFactory,
    ClassroomFactory,
    ClassroomEnrollmentFactory,
    USER_PASSWORD,
)
from test_utils.response import MockResponse


logger = logging.getLogger(__name__)

FAKE_UUIDS = [str(uuid4()) for i in range(5)]
FAKE_USER_ID = 1


def _jwt_payload_from_role_context_pairs(user, role_context_pairs):
    """
    Generates a new JWT payload with roles assigned from pairs of (role name, context).
    """
    roles = []
    for role, context in role_context_pairs:
        role_data = f"{role}"
        if context is not None:
            role_data += f":{context}"
        roles.append(role_data)

    payload = generate_unversioned_payload(user)
    payload.update({"roles": roles})
    return payload


def _set_encoded_jwt_in_cookies(client, payload):
    """
    JWT-encodes the given payload and sets it in the client's cookies.
    """
    client.cookies[jwt_cookie_name()] = generate_jwt_token(payload)


def init_jwt_cookie(client, user, role_context_pairs=None, jwt_payload_extra=None):
    """
    Initialize a JWT token in the given client's cookies.
    """
    jwt_payload = _jwt_payload_from_role_context_pairs(user, role_context_pairs or [])
    jwt_payload.update(jwt_payload_extra or {})
    _set_encoded_jwt_in_cookies(client, jwt_payload)


@ddt.ddt
class ClassroomsViewSetTests(APITestCase):
    """
    Tests for the ClassroomsViewSet
    """

    def setUp(self) -> None:
        super().setUp()

        self.teacher_1 = UserFactory()
        self.teacher_2 = UserFactory()
        self.classroom_1 = ClassroomFactory.create(school=FAKE_UUIDS[0])
        self.classroom_2 = ClassroomFactory.create(school=FAKE_UUIDS[0])
        self.classroom_3 = ClassroomFactory.create(school=FAKE_UUIDS[0])
        self.classroom_4 = ClassroomFactory.create(school=FAKE_UUIDS[1])

        self.enrollment_1 = ClassroomEnrollmentFactory.create(
            classroom_instance=self.classroom_1, user_id=self.teacher_1.email
        )
        self.enrollment_2 = ClassroomEnrollmentFactory.create(
            classroom_instance=self.classroom_2, user_id=self.teacher_1.email
        )
        self.enrollment_3 = ClassroomEnrollmentFactory.create(
            classroom_instance=self.classroom_3, user_id=self.teacher_2.email
        )

        self.client.login(username=self.teacher_1, password=USER_PASSWORD)

        # Classroom URLs
        self.classroom_list_url = reverse("api:v1:classrooms-list")
        self.classroom_detail_url = reverse(
            "api:v1:classrooms-detail",
            kwargs={"classroom_uuid": self.classroom_1.uuid},
        )

        self.classroom_enroll_url = reverse(
            "api:v1:classrooms-enroll",
            kwargs={"classroom_uuid": str(self.classroom_1.uuid)},
        )

        self.courses_list_url = reverse(
            "api:v1:classrooms-courses",
            kwargs={"classroom_uuid": str(self.classroom_1.uuid)},
        )

    def test_unauthenticated_user_401(self):
        """Test that unauthenticated users receive a 401 from the classroom endpoint."""
        self.client.logout()

        response = self.client.get(self.classroom_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_403(self):
        """Test that users without JWT roles receive a 403 from the classroom endpoint."""
        # TODO Does the response need to change to hide implementation?

        # init a JWT cookie (so the user is authenticated) but don't provide any roles
        init_jwt_cookie(
            self.client,
            self.teacher_1,
        )

        response = self.client.get(self.classroom_list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_with_teacher_role(self):
        """Test that the autenticated user gets data"""

        # init a JWT cookie (so the user is authenticated) but don't provide any roles
        init_jwt_cookie(
            self.client,
            self.teacher_1,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom_1.school))],
        )

        response = self.client.get(self.classroom_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_access_classroom_detail(self):
        """Test that teachers can get details from their classrooms"""

        # init a JWT cookie (so the user is authenticated) but don't provide any roles
        init_jwt_cookie(
            self.client,
            self.teacher_1,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom_1.school))],
        )

        response = self.client.get(self.classroom_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_classroom(self):
        """
        Test POST classroom creates a classroom with the user as a teacher.
        """
        # TODO Classroom should not require explicit school UUID
        # init a JWT cookie (so the user is authenticated) with admin role
        init_jwt_cookie(
            self.client,
            self.teacher_1,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom_1.school))],
        )

        response = self.client.post(
            self.classroom_list_url,
            data=json.dumps(
                {
                    "name": "Jedis",
                    "school": FAKE_UUIDS[0],
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = json.loads(response.content)

        self.assertIsNotNone(response.get("uuid"))
        self.assertIsNotNone(response.get("classroom_uuid"))

    @ddt.data(
        {
            "name": "Year 9 - Science",
            "active": True,
        },
        {
            "name": "",
            "active": True,
        },
        {
            "name": "Year 10 - Maths",
            "active": False,
        },
        {
            "name": "Year 10 - Maths",
            "school": FAKE_UUIDS[1],
            "active": True,
        },
    )
    def test_update_classroom(self, request_data):
        """Test Classroom can be updated via PUT endpoint except for the school uuid"""

        school = (
            request_data.get("school")
            if request_data.get("school")
            else self.classroom_1.school
        )

        # init a JWT cookie (so the user is authenticated) with admin role
        init_jwt_cookie(
            self.client,
            self.teacher_1,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom_1.school))],
        )

        data = {
            "name": request_data.get("name"),
            "school": school,
            "active": request_data.get("active"),
        }

        response = self.client.put(self.classroom_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNot(request_data.get("school"), self.classroom_1.school)

        if data.get("name") == "":
            self.assertEqual(response.data.get("name"), self.classroom_1.name)
            self.assertIsNot(response.data.get("name"), data.get("name"))
        else:
            self.assertEqual(response.data.get("name"), data.get("name"))

    def test_delete_classroom(self):
        """Test DELETE endpoint returns 405 because we don't support it"""
        # init a JWT cookie (so the user is authenticated) with admin role
        init_jwt_cookie(
            self.client,
            self.teacher_1,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom_1.school))],
        )

        response = self.client.delete(self.classroom_detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_classroom(self):
        """Test PATCH endpoint returns 405 because we don't support it"""

        init_jwt_cookie(
            self.client,
            self.teacher_1,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom_1.school))],
        )

        response = self.client.patch(self.classroom_detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_enroll_users_in_classroom(self):
        """Test to enroll one or multiple users in a classroom"""

        # init a JWT cookie (so the user is authenticated) with admin role
        init_jwt_cookie(
            self.client,
            self.teacher_1,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom_1.school))],
        )

        # before = self.client.get(self.classroom_enrollments_list_url).data

        student_1 = UserFactory()
        student_2 = UserFactory()
        identifiers = student_1.email + "\n" + student_2.email

        data = {"identifiers": identifiers}

        response = self.client.post(self.classroom_enroll_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # after = self.client.get(self.classroom_enrollments_list_url).data

        # self.assertGreater(len(after), len(before))
        # self.assertIsNotNone(response.data.get("enrolled"))

    def test_get_course_list(self):
        """Test to get a list of courses"""

        # init a JWT cookie (so the user is authenticated) with admin role
        init_jwt_cookie(
            self.client,
            self.teacher_1,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom_1.school))],
        )

        response = self.client.get(self.courses_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


@ddt.ddt
class ClassroomEnrollmentViewSetTests(APITestCase):
    """
    Tests for the ClassroomEnrollmentViewSet
    """

    def setUp(self) -> None:
        super().setUp()

        self.teacher_1 = UserFactory()
        self.student_1 = UserFactory()
        self.student_2 = UserFactory()

        self.classroom_1 = ClassroomFactory.create(school=FAKE_UUIDS[0])
        self.classroom_2 = ClassroomFactory.create(school=FAKE_UUIDS[0])

        self.enrollment_1 = ClassroomEnrollmentFactory.create(
            classroom_instance=self.classroom_1,
            user_id=self.teacher_1.email,
            staff=True,
        )

        self.enrollment_2 = ClassroomEnrollmentFactory.create(
            classroom_instance=self.classroom_1,
            user_id=self.student_1.email,
            staff=False,
        )

        self.enrollment_3 = ClassroomEnrollmentFactory.create(
            classroom_instance=self.classroom_2,
            user_id=self.teacher_1.email,
            staff=True,
        )

        self.client.login(username=self.teacher_1, password=USER_PASSWORD)

        # init a JWT cookie (so the user is authenticated) with admin role
        init_jwt_cookie(
            self.client,
            self.teacher_1,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom_1.school))],
        )

        self.enrollments_list_url = reverse(
            "api:v1:enrollments-list",
            kwargs={"classroom_uuid": str(self.classroom_1.uuid)},
        )

    def test_get_all_enrollments_in_classroom(self):
        """Test get a list of enrollments in a classroom"""

        response = self.client.get(self.enrollments_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 2)

    # TODO test with bad request_data
    def test_create_single_enrollment(self):
        """Test POST endpoints creates a classroom enrollment"""
        request_data = {
            "user_id": self.student_2.email,
        }

        response = self.client.post(
            self.enrollments_list_url,
            data=json.dumps(request_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.enrollments_list_url)
        self.assertEqual(response.data.get("count"), 3)

    @ddt.data(1, 2)
    def test_get_single_enrollment(self, pk):
        """Test GET for a single enrollment"""
        # TODO Yikes

        list_response = self.client.get(self.enrollments_list_url)

        url = reverse(
            "api:v1:enrollments-detail",
            kwargs={
                "classroom_uuid": str(self.classroom_1.uuid),
                "id": pk,
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("user_id"),
            list_response.data["results"][pk - 1]["user_id"],
        )

    def test_delete_single_enrollment(self):
        """Test DELETE"""
        response = self.client.get(self.enrollments_list_url)

        self.assertEqual(response.data.get("count"), 2)

        url = reverse(
            "api:v1:enrollments-detail",
            kwargs={
                "classroom_uuid": self.classroom_1.uuid,
                "id": response.data.get("results")[1]["pk"],
            },
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.enrollments_list_url)

        self.assertEqual(response.data.get("count"), 1)

    # TODO test bulk enrollments
    # TODO What if there is only 1 enrollment left in the classroom?
    # def test_delete_last_enrollment(self):


@ddt.ddt
class CourseAssignmentViewsetTests(APITestCase):
    """
    Tests for the CourseAssignmentViewset
    """

    @mock.patch("classrooms.apps.api_client.base_oauth.OAuthAPIClient")
    def setUp(self, mock_oauth_client) -> None:

        self.teacher_1 = UserFactory()

        self.course_ids = [
            "course-v1:DiceyTech+BOX001+TEMPLATE",
            "course-v1:DiceyTech+EXP001+TEMPLATE",
        ]

        self.classroom = ClassroomFactory.create(school=FAKE_UUIDS[0])

        self.expected_course_run = (
            self.classroom.name.replace(" ", "")
            + "_"
            + date.today().strftime(constants.DATE_FORMAT)
        )

        self.expected_course_id = self.course_ids[0].replace(
            "TEMPLATE", self.expected_course_run
        )

        mock_oauth_client.return_value.post.return_value = MockResponse(
            json_data={"key": self.expected_course_id},
            status_code=status.HTTP_201_CREATED,
        )

        self.course_assignment = CourseAssignmentFactory.create(
            course_id=self.course_ids[0], classroom_instance=self.classroom
        )

        self.client.login(username=self.teacher_1, password=USER_PASSWORD)

        # init a JWT cookie (so the user is authenticated) with admin role
        init_jwt_cookie(
            self.client,
            self.teacher_1,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom.school))],
        )

        self.assignment_list_url = reverse(
            "api:v1:assignments-list",
            kwargs={"classroom_uuid": str(self.classroom.uuid)},
        )

        super().setUp()

    def test_get_all_assignments_in_classroom(self):
        """Test get a list of assignments in a classroom"""

        response = self.client.get(self.assignment_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 1)
