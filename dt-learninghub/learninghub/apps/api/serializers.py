"""
Serializers for REST API endpoints
"""

from re import L
from rest_framework import serializers

from learninghub.apps.classrooms.models import (
    Classroom,
    ClassroomEnrollment,
    CourseAssignment,
)


class ClassroomSerializer(serializers.ModelSerializer):
    """Serializes the Classroom object"""

    class Meta:
        model = Classroom
        fields = ["uuid", "name", "active", "school"]
        read_only_fields = ["uuid"]


class ClassroomEnrollmentSerializer(serializers.ModelSerializer):
    """Serializes the ClassroomEnrollment object"""

    class Meta:
        model = ClassroomEnrollment
        fields = ["pk", "classroom_instance", "user_id", "staff"]
        lookup_field = "user_id"

    def to_representation(self, instance):
        """
        Return a formatted representation of the
        classroom enrollment
        """

        ret = {
            "pk": instance.pk,
            "classroom_uuid": str(instance.classroom_instance.uuid),
            "user_id": instance.user_id,
        }

        return ret


class CourseAssignmentSerializer(serializers.ModelSerializer):
    """Serialises the CourseAssignment object"""

    class Meta:
        model = CourseAssignment
        fields = ["course_id", "classroom_instance"]
