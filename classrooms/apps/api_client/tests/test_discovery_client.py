""" Tests for discovery api client """
from unittest import mock
from unittest.case import expectedFailure

from django.test import TestCase

from classrooms.apps.api_client.discovery import DiscoveryApiClient


class TestDiscoveryApiClient(TestCase):
    """DiscoveryApiClient tests."""

    @mock.patch("classrooms.apps.api_client.base_oauth.OAuthAPIClient")
    def test_create_course_run(self, mock_oauth_client):
        """ """

        course_data = {
            "start": "2021-09-18T14:40",
            "end": "2021-12-18T14:40",
            "pacing_type": "self_paced",
            "run_type": "1cfaba8e-16c2-4342-addd-4937b38c05ce",
            "status": "published",
            "course": "DiceyTech+DT002",
            "term": "Y7Computing_092021",
        }

        expected_course_key = f"course-v1:{course_data.get('course')}+TEST"

        mock_oauth_client.return_value.post.return_value = {
            "results": [{"key": expected_course_key}]
        }

        client = DiscoveryApiClient()

        actual_response = client.create_course_run(course_data)

        mock_oauth_client.return_value.post.assert_called_once()

        expected_response = {"results": [{"key": expected_course_key}]}
        self.assertEqual(expected_response, actual_response)
