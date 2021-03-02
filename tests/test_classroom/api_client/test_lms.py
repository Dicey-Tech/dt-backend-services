# -*- coding: utf-8 -*-
"""
Tests for classroom.api_client.lms.py
"""
from pytest import raises
from django.test import TestCase

from classroom.utils import NotConnectedToOpenEdX
from classroom.api_client.lms import JwtLmsApiClient


class TestJwtLmsApiClient(TestCase):
    """
    Test JwtLmsApiClient
    """

    def test_jwt_lms_api_client_locally_raises(self):
        with raises(NotConnectedToOpenEdX):
            client = JwtLmsApiClient("user-goes-here")
            client.connect()

    # def test_jwt_lms_api_client_refresh_token(self):
