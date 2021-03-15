"""
Viewsets
"""

from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response

from classroom.apps.api.serializers import (
    ClassroomSerializer,
    ClassroomEnrollementSerializer,
)
from classroom.apps.classroom.models import Classroom, ClassroomEnrollement


class ClassroomsViewSet(viewsets.ModelViewSet):
    """
    Classroom view to:
        - list classroom data (GET .../)
        - retrieve single classroom (GET .../<short_name>)
        - create an classroom via the POST endpoint (POST .../)
        - update an classroom via the PUT endpoint (PUT .../<short_name>)
    """

    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    # lookup_field
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


class ClassroomEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = ClassroomEnrollement.objects.all()
    serializer_class = ClassroomEnrollementSerializer
    permission_classes = [permissions.IsAuthenticated]
