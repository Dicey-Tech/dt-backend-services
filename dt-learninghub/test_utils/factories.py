"""
Provides factory for API Tests.
"""
from uuid import uuid4

import factory
from factory.django import DjangoModelFactory
from learninghub.apps.classrooms.models import (
    Classroom,
    ClassroomEnrollment,
    CourseAssignment,
)
from learninghub.apps.core.models import User

USER_PASSWORD = "password"

factory.Faker.override_default_locale("en_GB")


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
        model = ClassroomEnrollment

    classroom_instance = factory.SubFactory(ClassroomFactory)
    lms_user_id = 1
    user_email = "test@test.com"
    staff = False


class CourseAssignmentFactory(DjangoModelFactory):
    """Course assignments creation factory"""

    class Meta:
        model = CourseAssignment

    course_id = "course-v1:DiceyTech+BOX001+PRTHRN_July_2021"
    classroom_instance = factory.SubFactory(ClassroomFactory)
