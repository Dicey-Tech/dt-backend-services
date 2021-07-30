"""
Views for classroom end points.
"""

import logging

from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import status, viewsets, permissions
from rest_framework.exceptions import ValidationError, ParseError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from edx_rbac.mixins import PermissionRequiredForListingMixin

from classroom.apps.api.serializers import (
    ClassroomSerializer,
    ClassroomEnrollementSerializer,
)
from classroom.apps.classroom.models import (
    Classroom,
    ClassroomEnrollement,
    ClassroomRoleAssignment,
)
from classroom.apps.classroom import constants

logger = logging.getLogger(__name__)


class ClassroomsViewSet(PermissionRequiredForListingMixin, viewsets.ModelViewSet):
    """
    Classroom view to:
        - list classroom data (GET .../)
        - retrieve single classroom (GET .../<uuid>)
        - create a classroom via the POST endpoint (POST .../)
        - update a classroom via the PUT endpoint (PUT .../<uuid>)
    """

    authentication_classes = [JwtAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    lookup_field = "uuid"
    serializer_class = ClassroomSerializer
    enrollment_serializer_class = ClassroomEnrollementSerializer
    permission_required = constants.CLASSROOM_TEACHER_ACCESS_PERMISSION

    # fields that control permissions for 'list' actions
    list_lookup_field = "school"
    allowed_roles = [constants.CLASSROOM_TEACHER_ROLE]
    role_assignment_class = ClassroomRoleAssignment

    @property
    def base_queryset(self):
        """
        Required by the `PermissionRequiredForListingMixin`.
        For non-list actions, this is what's returned by `get_queryset()`.
        For list actions, some non-strict subset of this is what's returned by `get_queryset()`.
        """
        # TODO get the school/enterprise uuid of the user and use it get all classroom
        # linked ot their school.
        """
        kwargs = {}
        if self.requested_school_uuid:
            kwargs.update({"school": self.requested_school_uuid})
        if self.requested_classroom_uuid:
            kwargs.update({"uuid": self.requested_classroom_uuid})
        logger.debug(f"base_queryset: {kwargs}")
        """
        return Classroom.objects.all()

    @property
    def requested_school_uuid(self):

        if self.requested_classroom_uuid:
            school_uuid = Classroom.objects.get(
                uuid=self.requested_classroom_uuid
            ).school
        else:
            school_uuid = self.request.data.get("school")

        logger.debug(f"requested_school_uuid: {school_uuid}")

        if not school_uuid:
            return None
        try:
            return school_uuid
        except ValueError as exc:
            raise ParseError(f"{school_uuid} is not a valid uuid.") from exc

    @property
    def requested_classroom_uuid(self):
        return self.kwargs.get("uuid")

    def create(self, request, *args, **kwargs):
        """
        Creating a classroom also trigger an classroom enrollment for the teacher
        """
        classroom_data = self.serializer_class(data=request.data)
        classroom_data.is_valid(raise_exception=True)
        classroom_data.save()

        enrollment_data = {
            "classroom_id": classroom_data.data["uuid"],
            "user_id": request.user.id,
        }

        enrollment_serializer = self.enrollment_serializer_class(data=enrollment_data)
        enrollment_serializer.is_valid(raise_exception=True)
        enrollment_serializer.save()

        return Response(
            {
                **classroom_data.data,
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

        classroom_data = self.serializer_class(instance=classroom, data=data)
        classroom_data.is_valid(raise_exception=True)
        classroom_data.save()
        return Response(classroom_data.data, status=status.HTTP_200_OK)

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

    def get_permission_object(self):
        """
        Retrieves the apporpriate user object to use during edx-rbac's permission checks.
        This object is passed to the rule predicate(s).

        The requesting user needs to be part of a school to have access to the classroom
        feature.
        """
        logger.debug(f"Get data from request: {str(self.kwargs.get('uuid'))}")

        return self.requested_school_uuid


class ClassroomEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = ClassroomEnrollement.objects.all()
    serializer_class = ClassroomEnrollementSerializer
    permission_classes = [permissions.IsAuthenticated]
