"""
Serializers for REST API endpoints
"""

from rest_framework import serializers

from classroom.apps.classroom.models import Classroom, ClassroomEnrollement


class ClassroomSerializer(serializers.ModelSerializer):
    """ Serializes the Classroom object """

    class Meta:
        model = Classroom
        fields = ["uuid", "school", "name", "active"]
        read_only_fields = ["uuid"]


class ClassroomEnrollementSerializer(serializers.ModelSerializer):
    """ Serializes the ClassroomEnrollement object """

    class Meta:
        model = ClassroomEnrollement
        fields = ["classroom_id", "user_id", "active"]