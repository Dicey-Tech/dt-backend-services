"""
Classroom API Test Cases
"""
import json
from uuid import uuid4
import ddt

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from classroom.apps.api.tests.factories import (
    UserFactory,
    ClassroomFactory,
)

FAKE_UUIDS = [str(uuid4()) for i in range(5)]
FAKE_USER_ID = 1


@ddt.ddt
class ClassroomsViewSetTests(APITestCase):
    """
    Tests for the ClassroomCRUDViewSet
    """

    def setUp(self) -> None:
        super().setUp()

        self.user = UserFactory(is_superuser=True)
        # self.client.login(username=self.user, password=USER_PASSWORD)
        self.client.force_login(self.user)
        self.classroom_list_url = reverse("api:v1:classrooms-list")
        self.classroom = ClassroomFactory.create()

    def test_authenticaion_required(self):
        """ Test that authentication is required to access view """
        # TODO Does the response need to change to hide implementation?
        self.client.logout()
        response = self.client.get(self.classroom_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user(self):
        """ Test that the autenticated user gets data """
        ClassroomFactory.create()
        response = self.client.get(self.classroom_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

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
        response = self.client.post(
            self.classroom_list_url,
            data=json.dumps(request_data),
            content_type="application/json",
        )

        try:
            if request_data["school"]:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                response = json.loads(response.content)

                self.assertIsNotNone(response["uuid"])
                self.assertEqual(response["uuid"], response["teacher_enrollment"])
        except KeyError:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        """ Test Classroom can be updated via PUT endpoint except for the school uuid """
        try:
            data = {
                "name": request_data["name"],
                "school": request_data["school"],
                "active": request_data["active"],
            }
        except KeyError:
            data = {
                "name": request_data["name"],
                "school": self.classroom.school,
                "active": request_data["active"],
            }

        url = reverse(
            "api:v1:classrooms-detail", kwargs={"uuid": str(self.classroom.uuid)}
        )

        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNot(response.data["school"], FAKE_UUIDS[1])

        if data["name"] == "":
            self.assertEqual(response.data["name"], self.classroom.name)
            self.assertIsNot(response.data["name"], data["name"])
        else:
            self.assertEqual(response.data["name"], data["name"])

    def test_delete_classroom(self):
        """ Test DELETE endpoint returns 405 because we don't support it """
        url = reverse(
            "api:v1:classrooms-detail", kwargs={"uuid": str(self.classroom.uuid)}
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_classroom(self):
        """ Test PATCH endpoint returns 405 because we don't support it """
        url = reverse(
            "api:v1:classrooms-detail", kwargs={"uuid": str(self.classroom.uuid)}
        )

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
