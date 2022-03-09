""" Tests for lms api client """
from unittest import mock

import ddt
from django.test import TestCase
from learninghub.apps.api_client.lms import LMSApiClient
from test_utils.response import MockResponse


@ddt.ddt
class TestLMSApiClient(TestCase):
    """LMSApiClient Tests"""

    @ddt.data(
        (
            ["course-v1:DiceyTech+DT002+Y7Computing_092021"],
            ["student1@school1.co.uk"],
        ),
        (
            [
                "course-v1:DiceyTech+DT002+Y7Computing_092021",
                "course-v1:DiceyTech+DT002+Y7Computing_102021",
            ],
            "student1@school1.co.uk",
        ),
        (
            ["course-v1:DiceyTech+DT002+Y7Computing_102021"],
            [
                "student1@school1.co.uk",
                "student2@school1.co.uk",
            ],
        ),
        (
            [
                "course-v1:DiceyTech+DT002+Y7Computing_092021",
                "course-v1:DiceyTech+DT002+Y7Computing_102021",
            ],
            [
                "student1@school1.co.uk",
                "student2@school1.co.uk",
            ],
        ),
    )
    @ddt.unpack
    @mock.patch("learninghub.apps.api_client.base_oauth.OAuthAPIClient")
    def test_bulk_enroll(self, courses, students, mock_oauth_client):
        """Test bulk enroll endpoint
                TODO Use realistic response result assert See the `instructor.views.api.students_update_enrollment`
        docstring for the specifics of the response data available for each
        enrollment)
        """

        mock_oauth_client.return_value.post.return_value = MockResponse(
            {"data": "data"}, 201
        )

        client = LMSApiClient()

        response = client.bulk_enroll(courses=courses, identifiers=students)

        mock_oauth_client.return_value.post.assert_called_once()
