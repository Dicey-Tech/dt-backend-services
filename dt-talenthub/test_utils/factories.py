"""
Provides factory for API Tests.
"""

import factory
from factory.django import DjangoModelFactory

from talenthub.apps.core.models import User
from talenthub.apps.demographics.models import UserDemographics


USER_PASSWORD = "password"


class UserFactory(DjangoModelFactory):
    """User creation factory"""

    class Meta:
        model = User
        django_get_or_create = ("email", "username")

    username = factory.Faker("user_name")
    password = factory.PostGenerationMethodCall("set_password", USER_PASSWORD)
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False


class UserDemographicsFactory(DjangoModelFactory):
    """User profiles creating factory"""

    class Meta:
        model = UserDemographics

    user = 1
    gender = "f"
    user_ethnicity = ["Asian - Asia"]
