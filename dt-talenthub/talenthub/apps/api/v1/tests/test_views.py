"""
Talenthub API Test Cases

TODO Add authorization layer
"""

import json
import logging

import ddt
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from test_utils.factories import UserFactory, UserDemographicsFactory
from talenthub.apps.demographics.models import UserDemographics

logger = logging.getLogger(__name__)
USER_ID = 1


@ddt.ddt
class DemographicsViewSetTests(APITestCase):
    """
    Tests for the DemographicsViewSet
    """

    def setUp(self) -> None:
        super().setUp()

        self.user_1 = UserFactory(id=USER_ID)
        self.profile = UserDemographicsFactory.create(
            user=self.user_1.id,
            gender=UserDemographics.GenderChoices.MALE,
            user_ethnicity=UserDemographics.EthnicityChoices.BLACK_AFRICAN,
        )

        self.demographics_list_url = reverse("api:v1:demographics-list")
        self.demographics_detail_url = reverse(
            "api:v1:demographics-detail", kwargs={"user": self.user_1.id}
        )

    @ddt.data(
        {
            "user": 7,
            "gender": "m",
            "gender_description": "",
            "income": "",
            "learner_education_level": "",
            "parent_education_level": "",
            "military_history": "",
            "work_status": "",
            "work_status_description": "",
            "current_work_sector": "",
            "future_work_sector": "",
            "user_ethnicity": "",
        },
        {
            "user": "",
            "gender": "",
            "gender_description": "",
            "income": "",
            "learner_education_level": "",
            "parent_education_level": "",
            "military_history": "",
            "work_status": "",
            "work_status_description": "",
            "current_work_sector": "",
            "future_work_sector": "",
            "user_ethnicity": "",
        },
    )
    def test_create_user_demographic_profile(self, user_data) -> None:
        """Test POST demographics of demographics data for a single user"""

        if not user_data["user"]:
            user_data["user"] = self.user_1.id

        response = self.client.post(
            self.demographics_list_url,
            data=json.dumps(user_data),
            content_type="application/json",
        )

        if user_data["user"] == self.user_1.id:
            # Fail if the user already has a demographic profile
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        else:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            url = reverse(
                "api:v1:demographics-detail", kwargs={"user": user_data["user"]}
            )
            profile = self.client.get(url)

            self.assertEqual(profile.data["user"], user_data["user"])
            self.assertEqual(profile.data["gender"], user_data["gender"])

    @ddt.data(USER_ID, 3)
    def test_get_user_demographic_profile(self, user_id) -> None:
        """Test GET demographics profile"""

        url = reverse("api:v1:demographics-detail", kwargs={"user": user_id})

        response = self.client.get(url)

        if user_id == self.user_1.id:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["user"], USER_ID)
        else:
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @ddt.data(USER_ID)
    def test_patch_demographic_profile(self, user_id) -> None:
        """Test PATCH demographics profile"""
        old_data = str(self.profile.gender)

        data = {
            "gender": str(UserDemographics.GenderChoices.FEMALE),
        }

        url = reverse("api:v1:demographics-detail", kwargs={"user": user_id})

        response = self.client.patch(url, data=data)
        self.profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["gender"], old_data)

    @ddt.data(USER_ID)
    def test_update_demographic_profile(self, user_id):
        """Test UPDATE demographics profile"""

        old_data = str(self.profile.gender)

        data = {
            "user": user_id,
            "gender": str(UserDemographics.GenderChoices.FEMALE),
            "user_ethnicity": str(self.profile.user_ethnicity),
            "education_level": str(self.profile.education_level)
            if self.profile.education_level
            else "",
        }

        url = reverse("api:v1:demographics-detail", kwargs={"user": user_id})

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["gender"], old_data)

    def test_delete_user_demographic_profile(self):
        """Test DELETE endpoint returns 405 because we don't support it"""

        response = self.client.delete(self.demographics_detail_url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
