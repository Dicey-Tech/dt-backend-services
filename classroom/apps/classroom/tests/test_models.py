"""
Tests for the `classroom` models module.
"""

from uuid import uuid4
import ddt

from pytest import mark
from django.test import TestCase

from classroom.apps.classroom.models import ClassroomInstance


@mark.django_db
@ddt.ddt
class TestClassroomInstance(TestCase):
    """
    Tests for the ClassroomInstance model.
    """

    def setUp(self) -> None:
        self.name = "Demo Class"
        self.school = uuid4()
        self.classroom_instance = ClassroomInstance.objects.create(
            name=self.name,
            school=self.school,
        )
        super().setUp()

    @ddt.data(str, repr)
    def test_string_conversion(self, method):
        """
        Test conversion to string
        """
        expected_str = (
            f"<ClassroomInstance {self.name} with ID {self.classroom_instance.uuid}>"
        )
        self.assertEqual(expected_str, method(self.classroom_instance))
