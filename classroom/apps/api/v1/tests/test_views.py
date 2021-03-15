"""
Tests
"""
import json
from os import stat
from uuid import uuid4
import ddt

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

FAKE_UUIDS = [str(uuid4()) for i in range(5)]
FAKE_USER_ID = 1


@ddt.ddt
class ClassroomsViewSetTests(APITestCase):
    """
    Tests for the ClassroomCRUDViewSet
    """

    def setUp(self) -> None:
        self.endpoint = reverse("api:v1:classrooms-list")
        self.user = get_user_model().objects.create_user(
            "teacher@school.com",
            "Teacher",
        )
        self.client.force_login(self.user)
        super().setUp()

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
            self.endpoint,
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
