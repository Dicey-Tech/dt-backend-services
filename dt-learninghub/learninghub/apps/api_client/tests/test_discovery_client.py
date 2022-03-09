""" Tests for discovery api client """
from unittest import mock
import ddt

from django.test import TestCase

from learninghub.apps.api_client.discovery import DiscoveryApiClient
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
    @mock.patch("learninghub.apps.api_client.base_oauth.OAuthAPIClient")
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
    @mock.patch("learninghub.apps.api_client.base_oauth.OAuthAPIClient")
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

    # TODO test_get_course_list
    """
      "course_runs": [
        {
            "key": "course-v1:DiceyTech+EXP001+TEMPLATE",
            "uuid": "ee27844d-fd85-46eb-ae6a-fff649094ab1",
            "title": "RPS",
            "external_key": null,
            "image": {
            "src": "http://local.overhang.io/asset-v1:DiceyTech+EXP001+TEMPLATE+type@asset+block@Rock_Paper_Scissors_Project_Cover.png",
            "description": null,
            "height": null,
            "width": null
            },
            "short_description": null,
            "marketing_url": "course/rps-course-v1diceytechexp001template?utm_source=sofiane&utm_medium=affiliate_partner",
            "seats": [
                {
                    "type": "honor",
                    "price": "0.00",
                    "currency": "USD",
                    "upgrade_deadline": null,
                    "credit_provider": null,
                    "credit_hours": null,
                    "sku": "A947FB2",
                    "bulk_sku": null
                }
            ],
            "start": "2030-01-01T00:00:00Z",
            "end": null,
            "go_live_date": null,
            "enrollment_start": null,
            "enrollment_end": null,
            "pacing_type": "instructor_paced",
            "type": "honor",
            "run_type": "1cfaba8e-16c2-4342-addd-4937b38c05ce",
            "status": "published",
            "is_enrollable": true,
            "is_marketable": true,
            "course": "DiceyTech+EXP001",
            "full_description": null,
            "announcement": null,
            "video": null,
            "content_language": null,
            "license": "",
            "outcome": null,
            "transcript_languages": [],
            "instructors": [],
            "staff": [],
            "min_effort": null,
            "max_effort": null,
            "weeks_to_complete": null,
            "modified": "2021-09-27T10:41:55.233173Z",
            "level_type": null,
            "availability": "Upcoming",
            "mobile_available": false,
            "hidden": false,
            "reporting_type": "mooc",
            "eligible_for_financial_aid": true,
            "first_enrollable_paid_seat_price": null,
            "has_ofac_restrictions": null,
            "ofac_comment": "",
            "enrollment_count": 0,
            "recent_enrollment_count": 0,
            "expected_program_type": null,
            "expected_program_name": "",
            "course_uuid": "17df0b65-c588-4608-9edc-1fa3fdbcc2d6",
            "estimated_hours": 0,
            "content_language_search_facet_name": null
        }]
    """
