""" Tests for discovery api client """
from unittest import mock
import ddt

from django.test import TestCase

from classrooms.apps.api_client.discovery import DiscoveryApiClient
from test_utils.response import MockResponse


@ddt.ddt
class TestDiscoveryApiClient(TestCase):
    """DiscoveryApiClient tests."""

    @ddt.data(
        (
            201,
            {"key": "course-v1:DiceyTech+DT002+Y7Computing_092021"},
        ),
    )
    @ddt.unpack
    @mock.patch("classrooms.apps.api_client.base_oauth.OAuthAPIClient")
    def test_create_course_run(
        self, expected_status_code, expected_result, mock_oauth_client
    ):
        """
        Test create a course run
        TODO Test exception 400 "Failed to set course run data: Course matching query does not exist."
        """

        course_data = {
            "start": "2021-09-18T14:40",
            "end": "2021-12-18T14:40",
            "pacing_type": "self_paced",
            "run_type": "1cfaba8e-16c2-4342-addd-4937b38c05ce",
            "status": "published",
            "course": "DiceyTech+DT002",
            "term": "Y7Computing_092021",
        }

        mock_oauth_client.return_value.post.return_value = MockResponse(
            expected_result, expected_status_code
        )

        client = DiscoveryApiClient()

        actual_response = client.create_course_run(course_data)

        mock_oauth_client.return_value.post.assert_called_once()

        self.assertEqual(actual_response, expected_result)

    @ddt.data(
        (
            200,
            "DiceyTech+EXP001+TEMPLATE",
            {
                "count": 1,
                "next": "null",
                "previous": "null",
                "results": [
                    {
                        "key": "course-v1:DiceyTech+EXP001+TEMPLATE",
                        "run_type": "1cfaba8e-16c2-4342-addd-4937b38c05ce",
                    },
                ],
            },
        )
    )
    @ddt.unpack
    @mock.patch("classrooms.apps.api_client.base_oauth.OAuthAPIClient")
    def test_get_course_run_type(
        self, expected_status_code, course_key, expeced_result, mock_oauth_client
    ):
        """Test get course run type UUID for a given course run key"""

        mock_oauth_client.return_value.get.return_value = MockResponse(
            expeced_result, expected_status_code
        )

        client = DiscoveryApiClient()

        actual_run_type = client.get_course_run_type(course_key)

        mock_oauth_client.return_value.get.assert_called_once()

        self.assertEqual(
            expeced_result.get("results")[0].get("run_type"), actual_run_type
        )
