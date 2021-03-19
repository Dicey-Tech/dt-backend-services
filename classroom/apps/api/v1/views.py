"""
Views for classroom end points.
"""

from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import status, viewsets, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from classroom.apps.api.serializers import (
    ClassroomSerializer,
    ClassroomEnrollementSerializer,
)
from classroom.apps.classroom.models import Classroom, ClassroomEnrollement


class ClassroomsViewSet(viewsets.ModelViewSet):
    """
    Classroom view to:
        - list classroom data (GET .../)
        - retrieve single classroom (GET .../<uuid>)
        - create an classroom via the POST endpoint (POST .../)
        - update an classroom via the PUT endpoint (PUT .../<uuid>)
    """

    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    lookup_field = "uuid"
    # authentication_classes = [JwtAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Creating a classroom also trigger an classroom enrollment for the teacher
        """
        classroom_serializer = ClassroomSerializer(data=request.data)
        classroom_serializer.is_valid(raise_exception=True)
        classroom_serializer.save()

        enrollment_data = {
            "classroom_id": classroom_serializer.data["uuid"],
            "user_id": request.user.id,
        }
        enrollment_serializer = ClassroomEnrollementSerializer(data=enrollment_data)
        enrollment_serializer.is_valid(raise_exception=True)
        enrollment_serializer.save()

        return Response(
            {
                **classroom_serializer.data,
                "teacher_enrollment": enrollment_serializer.data["classroom_id"],
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """
        Update a classroom data.

        The 'school' may not be specified via the HTTP API since it can only be
        assigned when the classroom is created.
        """
        classroom = get_object_or_404(Classroom, uuid=kwargs.get("uuid"))

        name = (
            request.data.get("name")
            if not request.data.get("name") == ""
            else classroom.name
        )

        data = {
            "school": classroom.school,
            "name": name,
            "active": request.data.get("active", classroom.active),
        }

        classroom_serializer = ClassroomSerializer(instance=classroom, data=data)
        classroom_serializer.is_valid(raise_exception=True)
        classroom_serializer.save()
        return Response(classroom_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        We disable DELETE because all classromms should be kept and deactivated to be
        archived.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        """
        We disable DELETE because all classromms should be kept and deactivated to be
        archived.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ClassroomEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = ClassroomEnrollement.objects.all()
    serializer_class = ClassroomEnrollementSerializer
    permission_classes = [permissions.IsAuthenticated]
