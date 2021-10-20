""" Tests for studio api client  """
from unittest import mock
import ddt

from django.test import TestCase
from rest_framework import status

from classrooms.apps.api_client.studio import StudioApiClient
from test_utils.response import MockResponse


@ddt.ddt
class TestSutdioApiClient(TestCase):
    """StudioApiClient tests"""

    @ddt.data(
        (
            200,
            {
                "schedule": {
                    "start": "2021-10-19T00:00:00+01:00",
                    "end": "2022-01-20T23:59:00Z",
                    "enrollment_start": None,
                    "enrollment_end": None,
                },
                "pacing_type": "self_paced",
                "team": [{"user": "classroom", "role": "instructor"}],
                "id": "course-v1:DiceyTech+EXP003+Y11Testers_191021",
                "title": "Keychain",
                "images": {
                    "card_image": "http://studio.local.overhang.io:8001/asset-v1:DiceyTech+EXP003+Y11Testers_191021+type@asset+block@Keychain_Project_Cover.png"
                },
            },
        )
    )
    @ddt.unpack
    @mock.patch("classrooms.apps.api_client.base_oauth.OAuthAPIClient")
    def test_update_course_run(
        self, expected_status_code, expected_response_body, mock_oauth_client
    ):
        """Update a course run"""

        mock_oauth_client.return_value.patch.return_value = MockResponse(
            expected_response_body, expected_status_code
        )

        client = StudioApiClient()

        data_to_update = {
            "schedule": {
                "start": expected_response_body["schedule"]["start"],
                "end": expected_response_body["schedule"]["end"],
            },
        }

        response = client.update_course_run(
            expected_response_body["id"], data_to_update
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_response_body)
