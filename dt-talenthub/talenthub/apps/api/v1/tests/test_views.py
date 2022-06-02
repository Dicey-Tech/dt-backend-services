"""
Talenthub API Test Cases
"""

import json
import logging

import ddt
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from edx_rest_framework_extensions.auth.jwt.cookies import jwt_cookie_name
from edx_rest_framework_extensions.auth.jwt.tests.utils import (
    generate_jwt_token,
    generate_unversioned_payload,
)
from test_utils.factories import UserFactory, UserDemographicsFactory
from talenthub.apps.demographics.models import UserDemographics

logger = logging.getLogger(__name__)

ADMIN_ID = 1
USER_1_ID = 2
USER_2_ID = 3


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
class DemographicsViewSetTests(APITestCase):
    """
    Tests for the DemographicsViewSet
    """

    def setUp(self) -> None:
        super().setUp()

        self.user_1 = UserFactory(id=USER_1_ID)
        self.user_2 = UserFactory(id=USER_2_ID)
        self.admin_1 = UserFactory(id=ADMIN_ID, is_staff=True)

        self.profile_1 = UserDemographicsFactory.create(
            user=self.user_1.id,
            gender=UserDemographics.GenderChoices.MALE,
            user_ethnicity=UserDemographics.EthnicityChoices.BLACK_AFRICAN,
        )
        self.profile_2 = UserDemographicsFactory.create(
            user=self.user_2.id,
            gender=UserDemographics.GenderChoices.OTHER,
        )

        self.client.login(username=self.user_1.username, password=self.user_1.password)

        # init a JWT cookie (so the user is authenticated) but don't provide any roles
        init_jwt_cookie(
            self.client,
            self.user_1,
        )

        self.demographics_list_url = reverse("api:v1:demographics-list")
        self.demographics_detail_url = reverse(
            "api:v1:demographics-detail", kwargs={"user": self.user_1.id}
        )

    def test_unauthenticated_user_401(self) -> None:
        """Test unauthenticated users receive a 401 from the demograhpics endpoint."""
        self.client.logout()

        response = self.client.get(self.demographics_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_demographic_profiles(self) -> None:
        """Test only admin user can list all demographic profiles"""

        response = self.client.get(self.demographics_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        self.client.login(
            username=self.admin_1.username, password=self.admin_1.password
        )

        # init a JWT cookie (so the user is authenticated) but don't provide any roles
        init_jwt_cookie(
            self.client,
            self.admin_1,
        )
        response = self.client.get(self.demographics_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    @ddt.data(USER_1_ID, 4)
    def test_get_user_demographic_profile(self, USER_1_ID) -> None:
        """Test GET a specific user's demographic profile"""

        url = reverse("api:v1:demographics-detail", kwargs={"user": USER_1_ID})

        response = self.client.get(url)

        if USER_1_ID == self.user_1.id:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["user"], USER_1_ID)
        else:
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @ddt.data(USER_1_ID)
    def test_patch_demographic_profile(self, USER_1_ID) -> None:
        """Test PATCH demographics profile"""
        old_data = str(self.profile_1.gender)

        data = {
            "gender": str(UserDemographics.GenderChoices.FEMALE),
        }

        url = reverse("api:v1:demographics-detail", kwargs={"user": USER_1_ID})

        response = self.client.patch(url, data=data)
        self.profile_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["gender"], old_data)

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

    @ddt.data(USER_1_ID)
    def test_update_demographic_profile(self, USER_1_ID):
        """Test UPDATE demographics profile"""

        old_data = str(self.profile_1.gender)

        data = {
            "user": USER_1_ID,
            "gender": str(UserDemographics.GenderChoices.FEMALE),
            "user_ethnicity": str(self.profile_1.user_ethnicity),
            "education_level": str(self.profile_1.education_level)
            if self.profile_1.education_level
            else "",
        }

        url = reverse("api:v1:demographics-detail", kwargs={"user": USER_1_ID})

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["gender"], old_data)

    def test_delete_user_demographic_profile(self):
        """Test DELETE endpoint returns 405 because we don't support it"""

        response = self.client.delete(self.demographics_detail_url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
