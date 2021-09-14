""" Tests for enterprise api client. """
from unittest import mock
from uuid import uuid4

import ddt
from django.test import TestCase

from classrooms.apps.api_client.enterprise import EnterpriseApiClient
from classrooms.apps.api_client.constants import (
    ENTERPRISE_CUSTOMER_ENDPOINT,
    ENTERPRISE_LEARNER_ENDPOINT,
)


no_results = {
    "next": None,
    "previous": None,
    "count": 0,
    "num_pages": 1,
    "current_page": 1,
    "start": 0,
    "results": [],
}


@ddt.ddt
class TestEnterpriseApiClient(TestCase):
    """
    Tests for the edx-enterprise API client.
    """

    @mock.patch("classrooms.apps.api_client.base_oauth.OAuthAPIClient")
    @ddt.data(
        [],
        [
            {
                "name": "Test Enterprise",
                "slug": "test-enterprise",
                "active": True,
                "enable_learner_portal": True,
            },
        ],
    )
    def test_get_enterprise_customer(self, mock_response_results, mock_api_client):
        """
        Tests get_enterprise_customer when a customer record is or isn't found.
        """
        customer_uuid = uuid4()
        return_value = no_results
        return_value["count"] = len(mock_response_results)
        return_value["results"] = mock_response_results

        mock_api_client.return_value.get.return_value.json.return_value = return_value

        client = EnterpriseApiClient()
        customer_data = client.get_enterprise_customer(customer_uuid)

        mock_api_client.return_value.get.assert_called_with(
            ENTERPRISE_CUSTOMER_ENDPOINT, params={"uuid": customer_uuid}
        )

        if mock_response_results:
            self.assertEqual(customer_data, mock_response_results[0])
        else:
            self.assertEqual(customer_data, {})

    @mock.patch("classrooms.apps.api_client.base_oauth.OAuthAPIClient")
    @ddt.data(
        [],
        [
            {
                "user_id": 1,
                "user": {
                    "username": "test",
                    "first_name": "First Name",
                    "last_name": "Last Name",
                },
                "active": True,
            },
        ],
        [
            {
                "user_id": 1,
                "user": {
                    "username": "user1",
                    "first_name": "First Name",
                    "last_name": "Last Name",
                },
                "active": True,
            },
            {
                "user_id": 3,
                "user": {
                    "username": "user3",
                    "first_name": "First Name",
                    "last_name": "Last Name",
                },
                "active": True,
            },
        ],
    )
    def test_get_enterprise_learner(self, mock_response_results, mock_api_client):
        """
        Test get_enterprise_learners when learner record is or isn't found.
        """
        customer_uuid = uuid4()

        return_value = no_results
        return_value["count"] = len(mock_response_results)
        return_value["results"] = mock_response_results
        mock_api_client.return_value.get.return_value.json.return_value = return_value

        client = EnterpriseApiClient()
        learner_data = client.get_enterprise_learners(customer_uuid)

        mock_api_client.return_value.get.assert_called_with(
            ENTERPRISE_LEARNER_ENDPOINT, params={"uuid": customer_uuid}
        )

        if mock_response_results:
            self.assertEqual(learner_data, mock_response_results)
        else:
            self.assertEqual(learner_data, {})
