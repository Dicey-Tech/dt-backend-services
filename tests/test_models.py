#!/usr/bin/env python
"""
Tests for the `dt-classroom` models module.
"""
from pytest import mark
from django.test import TestCase

from classroom.models import Classroom


@mark.djang_db
class TestClassroom(TestCase):
    """
    Test classroom model
    """

    pass
    """
    # TODO Create a classroom
    def test_created_classroom_has_one_teacher(self):
        Classroom.objects.create(
            name="Year 8 Design & Engineering", teachers=EnterpriseCustomerUser()
        )
    """