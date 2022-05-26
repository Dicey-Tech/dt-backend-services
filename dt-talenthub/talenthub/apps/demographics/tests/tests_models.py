"""
Tests for the `demographics` models module.
"""

import ddt
from django.test import TestCase

from pytest import mark
from talenthub.apps.demographics.models import UserDemographics
from test_utils.factories import UserDemographicsFactory


@mark.django_db
@ddt.ddt
class TestUserDemographics(TestCase):
    """
    Tests for the UserDemographics model.
    """

    def setUp(self) -> None:
        self.user = 7
        self.gender = UserDemographics.GenderChoices.FEMALE
        self.user_ethnicity = UserDemographics.EthnicityChoices.BLACK_AFRICAN
        self.education_level = UserDemographics.EducationLevelChoices.MASTERS

        self.demographic_profile = UserDemographicsFactory.create(
            user=self.user,
            gender=self.gender,
            user_ethnicity=self.user_ethnicity,
            education_level=self.education_level,
        )
        super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, method) -> None:
        """
        Test conversion to string
        Args:
            method (method): _description_
        """

        expected_str = f"<UserDemographics for user with ID {self.user}>"
        self.assertEqual(expected_str, method(self.demographic_profile))
