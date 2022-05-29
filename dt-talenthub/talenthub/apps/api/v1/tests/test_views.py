"""
Talenthub API Test Cases

TODO Update demographic profile (patch)
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

    @ddt.data(
        {
            "user": 7,
            "demographics_gender": "",
            "demographics_gender_description": "",
            "demographics_income": "",
            "demographics_learner_education_level": "",
            "demographics_parent_education_level": "",
            "demographics_military_history": "",
            "demographics_work_status": "",
            "demographics_work_status_description": "",
            "demographics_current_work_sector": "",
            "demographics_future_work_sector": "",
            "demographics_user_ethnicity": [],
        },
        {
            "user": "",
            "demographics_gender": "",
            "demographics_gender_description": "",
            "demographics_income": "",
            "demographics_learner_education_level": "",
            "demographics_parent_education_level": "",
            "demographics_military_history": "",
            "demographics_work_status": "",
            "demographics_work_status_description": "",
            "demographics_current_work_sector": "",
            "demographics_future_work_sector": "",
            "demographics_user_ethnicity": [],
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

    @ddt.data(USER_ID, 3)
    def test_get_user_demographic_profile(self, user_id) -> None:
        """Test GET demographics profile"""

        self.demographics_detail_url = reverse(
            "api:v1:demographics-detail", kwargs={"user": user_id}
        )

        response = self.client.get(self.demographics_detail_url)

        if user_id == self.user_1.id:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["user"], USER_ID)
        else:
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TODO pytest talenthub/apps/api/v1/tests/test_views.py -k test_update_user_demographic_profile --no-cov
    def test_update_user_demographic_profile(self) -> None:
        """Test PATCH demographics profile"""

        pass
