"""
Tests for the `classroom` models module.
"""

from uuid import uuid4
import ddt

from pytest import mark
from django.test import TestCase

from classrooms.apps.classrooms.models import Classroom


@mark.django_db
@ddt.ddt
class TestClassroomInstance(TestCase):
    """
    Tests for the Classroom model.
    """

    def setUp(self) -> None:
        self.name = "Demo Class"
        self.uuid = uuid4()
        self.classroom_instance = Classroom.objects.create(
            name=self.name,
            school=self.uuid,
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
