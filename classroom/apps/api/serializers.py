"""
Serializers for REST API endpoints
"""
import re
from rest_framework import serializers

from classroom.apps.classroom.models import ClassroomInstance, ClassroomEnrollement


class ClassroomSerializer(serializers.Serializer):
    """
    Serializer for the `Classroom` model
    """

    classroom_uuid = serializers.UUIDField(read_only=True)
    school = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True)
    user_id = serializers.IntegerField(required=True)
    teacher_enrollment_id = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        """
        Create a ClassroomInstance and an enrollment for the teacher that
        created it.
        """
        classroom_instance = ClassroomInstance.objects.create(
            school=validated_data["school"], name=validated_data["name"]
        )

        validated_data["classroom_uuid"] = classroom_instance.uuid

        try:
            enrollment = ClassroomEnrollement.objects.create(
                classroom_instance_id=classroom_instance,
                user_id=validated_data["user_id"],
            )

            validated_data["teacher_enrollment_id"] = enrollment.pk
        except Exception as e:
            print(e)

        return validated_data
