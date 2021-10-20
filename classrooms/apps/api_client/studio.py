"""
Studio service API client
"""
import logging
from typing import Any, Dict
from rest_framework.response import Response
from rest_framework import status

from classrooms.apps.api_client.base_oauth import BaseOAuthClient
from classrooms.apps.api_client.constants import STUDIO_COURSE_RUNS_ENDPOINT

logger = logging.getLogger(__name__)


class StudioApiClient(BaseOAuthClient):
    """
    Object build an API client to make calls to the Studio service.
    """

    def update_course_run(
        self, course_id: str, coure_run_data: Dict[str, Any]
    ) -> Response:
        """Update course run details"""

        response = self.client.patch(
            STUDIO_COURSE_RUNS_ENDPOINT + course_id + "/", json=coure_run_data
        )

        response.raise_for_status()

        return response
