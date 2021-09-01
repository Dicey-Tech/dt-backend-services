"""
Serializers for REST API endpoints
"""

from rest_framework import serializers

from classroom.apps.classroom.models import Classroom, ClassroomEnrollement


class ClassroomSerializer(serializers.ModelSerializer):
    """Serializes the Classroom object"""

    class Meta:
        model = Classroom
        fields = ["uuid", "school", "name", "active"]
        read_only_fields = ["uuid"]


class ClassroomEnrollementSerializer(serializers.ModelSerializer):
    """Serializes the ClassroomEnrollement object"""

    class Meta:
        model = ClassroomEnrollement
        fields = ["classroom_instance", "user_id", "active"]

    def to_representation(self, instance):
        """
        Return a formatted representation of the
        classroom enrollment
        """

        ret = {
            "classroom_uuid": str(instance.classroom_instance.uuid),
            "user_id": instance.user_id,
        }

        return ret
