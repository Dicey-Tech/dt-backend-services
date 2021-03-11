"""
Tests
"""
import json
from uuid import uuid4
import ddt

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

FAKE_UUIDS = [str(uuid4()) for i in range(5)]
FAKE_USER_ID = 1


@ddt.ddt
class ClassroomCRUDViewSetTests(APITestCase):
    """
    Tests for the ClassroomCRUDViewSet
    """

    def setUp(self) -> None:
        self.endpoint = reverse("api:v1:classroom-list")
        super().setUp()

    @ddt.data(
        {
            "school": FAKE_UUIDS[0],
            "name": "Padawans",
            "user_id": FAKE_USER_ID,
        },
        {
            "name": "Jedis",
            "user_id": FAKE_USER_ID,
        },
        {
            "school": FAKE_UUIDS[1],
            "name": "Masters",
        },
    )
    def test_create_classroom(self, request_data):
        """
        Test POST classroom creates a classroom with the user as a teacher

        Create classroom is triggered by a teacher, so the new classroom needs to come with
        the enrollment of that teacher.
        # TODO User should be logged in and have sufficient status
        """

        response = self.client.post(self.endpoint, data=request_data)

        try:
            if request_data["school"] and request_data["user_id"]:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                response = json.loads(response.content)

                self.assertIsNotNone(response["classroom_uuid"])
                self.assertIsNotNone(response["teacher_enrollment_id"])
        except KeyError as e:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
