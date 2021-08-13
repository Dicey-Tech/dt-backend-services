"""
Provides factory for Tests.
"""
from uuid import uuid4
from django.utils.translation import activate

import factory
from factory.django import DjangoModelFactory

from classroom.apps.core.models import User
from classroom.apps.classroom.models import Classroom, ClassroomEnrollement

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


class ClassroomFactory(DjangoModelFactory):
    """Classroom creation factory"""

    class Meta:
        model = Classroom

    uuid = factory.LazyFunction(uuid4)
    name = factory.Faker("name")
    school = factory.LazyFunction(uuid4)
    active = True


class ClassroomEnrollmentFactory(DjangoModelFactory):
    """Classroom enrollment creation factory"""

    class Meta:
        model = ClassroomEnrollement

    classroom_instance = Classroom()
    user_id = 1
    active = True
