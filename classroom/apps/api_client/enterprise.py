from classroom.apps.api_client.base_oauth import BaseOAuthClient
from classroom.apps.api_client.constants import (
    ENTERPRISE_CUSTOMER_ENDPOINT,
    ENTERPRISE_LEARNER_ENDPOINT,
)


class EnterpriseApiClient(BaseOAuthClient):
    """
    API client for calls to the enterprise service.
    """

    def get_enterprise_customer(self, customer_uuid):
        """
        Retrieve an Enterprise Customer record from the edx-enterprise API.

        Arguments:
            customer_uuid: string representation of the customer's uuid

        Returns:
            enterprise_customer: dictionary record for customer with given uuid or
                                 empty dictionary if no customer record found
        """
        query_params = {"uuid": customer_uuid}

        response = self.client.get(
            ENTERPRISE_CUSTOMER_ENDPOINT, params=query_params
        ).json()

        results = response.get("results", [])
        enterprise_customer = results[0] if results else {}

        return enterprise_customer

    def get_enterprise_learners(self, customer_uuid):
        """
        Retrieve Enterprise Learner(s) record(s) from the edx-enterprise API.

        Arguments:
            customer_uuid: string representation of the customer's uuid

        Returns:
            enterprise_learner: dictionary record for learners with given uuid or
                                 empty dictionary if no learner record found
        """
        query_params = {"uuid": customer_uuid}

        response = self.client.get(
            ENTERPRISE_LEARNER_ENDPOINT, params=query_params
        ).json()

        results = response.get("results", [])
        learners_data = results if results else {}

        return learners_data
