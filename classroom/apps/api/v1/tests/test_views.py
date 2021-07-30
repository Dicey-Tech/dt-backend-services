"""
Classroom API Test Cases
"""
import json
from uuid import uuid4
import ddt

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from edx_rest_framework_extensions.auth.jwt.cookies import jwt_cookie_name
from edx_rest_framework_extensions.auth.jwt.tests.utils import (
    generate_jwt_token,
    generate_unversioned_payload,
)

from classroom.apps.classroom import constants
from classroom.apps.api.tests.factories import (
    UserFactory,
    ClassroomFactory,
)


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
    print(f"{jwt_cookie_name()}: f{generate_jwt_token(payload)}")
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
    Tests for the ClassroomCRUDViewSet
    """

    def setUp(self) -> None:
        super().setUp()

        self.user = UserFactory()
        # self.client.login(username=self.user, password=USER_PASSWORD)
        self.client.force_login(self.user)
        self.classroom_list_url = reverse("api:v1:classrooms-list")
        self.classroom = ClassroomFactory.create(school=FAKE_UUIDS[0])
        self.classroom_detail_url = reverse(
            "api:v1:classrooms-detail", kwargs={"uuid": self.classroom.uuid}
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
            self.user,
        )

        response = self.client.get(self.classroom_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_with_teacher_role(self):
        """Test that the autenticated user gets data"""

        # init a JWT cookie (so the user is authenticated) but don't provide any roles
        init_jwt_cookie(
            self.client,
            self.user,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom.school))],
        )

        response = self.client.get(self.classroom_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data), 1)

    def test_access_classroom_detail(self):
        """Test that a teacher can get details from her/his classrooms"""

        # init a JWT cookie (so the user is authenticated) but don't provide any roles
        init_jwt_cookie(
            self.client,
            self.user,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom.school))],
        )

        response = self.client.get(self.classroom_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @ddt.data(
        {
            "school": FAKE_UUIDS[0],
            "name": "Padawans",
        },
        {
            "name": "Jedis",
        },
        {
            "school": FAKE_UUIDS[0],
        },
    )
    def test_create_classroom(self, request_data):
        """
        Test POST classroom creates a classroom with the user as a teacher.
        # TODO User should be logged in and have sufficient permissions
        """
        # init a JWT cookie (so the user is authenticated) with admin role
        init_jwt_cookie(
            self.client,
            self.user,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom.school))],
        )

        response = self.client.post(
            self.classroom_list_url,
            data=json.dumps(request_data),
            content_type="application/json",
        )

        if not request_data.get("school"):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        else:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            response = json.loads(response.content)

            self.assertIsNotNone(response.get("uuid"))
            self.assertEqual(response.get("uuid"), response.get("teacher_enrollment"))

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
            else self.classroom.school
        )

        # init a JWT cookie (so the user is authenticated) with admin role
        init_jwt_cookie(
            self.client,
            self.user,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom.school))],
        )

        data = {
            "name": request_data.get("name"),
            "school": school,
            "active": request_data.get("active"),
        }

        url = reverse(
            "api:v1:classrooms-detail", kwargs={"uuid": str(self.classroom.uuid)}
        )

        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNot(request_data.get("school"), self.classroom.school)

        if data.get("name") == "":
            self.assertEqual(response.data.get("name"), self.classroom.name)
            self.assertIsNot(response.data.get("name"), data.get("name"))
        else:
            self.assertEqual(response.data.get("name"), data.get("name"))

    def test_delete_classroom(self):
        """Test DELETE endpoint returns 405 because we don't support it"""
        url = reverse(
            "api:v1:classrooms-detail", kwargs={"uuid": str(self.classroom.uuid)}
        )

        # init a JWT cookie (so the user is authenticated) with admin role
        init_jwt_cookie(
            self.client,
            self.user,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom.school))],
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_classroom(self):
        """Test PATCH endpoint returns 405 because we don't support it"""
        url = reverse(
            "api:v1:classrooms-detail", kwargs={"uuid": str(self.classroom.uuid)}
        )

        # init a JWT cookie (so the user is authenticated) with admin role
        init_jwt_cookie(
            self.client,
            self.user,
            [(constants.SYSTEM_ENTERPRISE_ADMIN_ROLE, str(self.classroom.school))],
        )

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
