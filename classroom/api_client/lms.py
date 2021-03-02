# -*- coding: utf-8 -*-
"""
Utilities to get connect to the lms REST API.
"""

import logging

from django.conf import settings

from classroom.utils import NotConnectedToOpenEdX

try:
    from openedx.core.djangoapps.oauth_dispatch import jwt as JwtBuilder
except ImportError:
    JwtBuilder = None


LOGGER = logging.getLogger(__name__)


class JwtLmsApiClient:
    """
    LMS client authenticates using a JSON Web Token (JWT) for the given user.
    """

    API_BASE = settings.LMS_INTERNAL_ROOT_URL + "/api/"

    def __init__(self, user, expires_in=settings.OAUTH_ID_TOKEN_EXPIRATION) -> None:
        """
        Connect to the REST API
        """
        self.user = user
        self.expires_in = expires_in
        self.expires_at = 0
        self.client = None

    def connect(self):
        """
        Connect to the REST API, authenticating with a JWT for the current user.
        """
        if JwtBuilder is None:
            raise NotConnectedToOpenEdX(
                "This package must be installed in an OpenEdX environment."
            )
