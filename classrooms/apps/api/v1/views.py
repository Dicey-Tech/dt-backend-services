"""
Views for classroom end points.
"""

import logging
import re

from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from edx_rbac.mixins import PermissionRequiredForListingMixin

from classrooms.apps.api.serializers import (
    ClassroomSerializer,
    ClassroomEnrollmentSerializer,
    CourseAssignmentSerializer,
)
from classrooms.apps.classrooms.models import (
    Classroom,
    ClassroomEnrollment,
    ClassroomRoleAssignment,
    CourseAssignment,
)
from classrooms.apps.classrooms import constants
from classrooms.apps.classrooms.utils import get_course_list

logger = logging.getLogger(__name__)


class ClassroomsViewSet(PermissionRequiredForListingMixin, viewsets.ModelViewSet):
    """
    Classroom view to:
        - list classroom data (GET .../)
        - retrieve single classroom (GET .../uuid)
        - create a classroom via the POST endpoint (POST .../)
        - update a classroom via the PUT endpoint (PUT .../<uuid>)
        - retrieve classroom enrollments (GET .../uuid/enrollments)
        - enroll users in the classroom (POST .../uuid/enroll
    """

    authentication_classes = [JwtAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    lookup_field = "uuid"
    lookup_url_kwarg = "classroom_uuid"

    serializer_class = ClassroomSerializer
    enrollment_serializer_class = ClassroomEnrollmentSerializer
    permission_required = constants.CLASSROOM_TEACHER_ACCESS_PERMISSION

    # fields that control permissions for 'list' actions
    list_lookup_field = "school"
    allowed_roles = [constants.CLASSROOM_TEACHER_ROLE]
    role_assignment_class = ClassroomRoleAssignment

    def _split_input_list(self, str_list):
        """
        Separate out individual student email from the comma, or space separated string.
        e.g.
        in: "Lorem@ipsum.dolor, sit@amet.consectetur\nadipiscing@elit.Aenean\r convallis@at.lacus\r, ut@lacinia.Sed"
        out: ['Lorem@ipsum.dolor', 'sit@amet.consectetur', 'adipiscing@elit.Aenean', 'convallis@at.lacus', 'ut@lacinia.Sed']
        `str_list` is a string coming from an input text area
        returns a list of separated values
        """

        new_list = re.split(r"[\n\r\s,]", str_list)
        new_list = [s.strip() for s in new_list]
        new_list = [s for s in new_list if s != ""]

        return new_list

    @property
    def base_queryset(self):
        """
        Required by the `PermissionRequiredForListingMixin`.
        For non-list actions, this is what's returned by `get_queryset()`.
        For list actions, some non-strict subset of this is what's returned by `get_queryset()`.

        Returns all classrooms that the user is enrolled in.
        """

        kwargs = {}
        if self.requested_school_uuid:
            kwargs.update({"school": self.requested_school_uuid})
        if self.requested_classroom_uuid:
            kwargs.update({"uuid": self.requested_classroom_uuid})

        enrollments = ClassroomEnrollment.objects.filter(
            user_id=self.request.user.email
        )

        classroom_ids = []
        for enrollment in enrollments:
            classroom_ids.append(enrollment.classroom_instance.uuid)

        return Classroom.objects.filter(uuid__in=classroom_ids)

    @property
    def requested_school_uuid(self):
        """
        Return school uuid
        """
        if self.requested_classroom_uuid:
            school_uuid = Classroom.objects.get(
                uuid=self.requested_classroom_uuid
            ).school
        else:
            school_uuid = self.request.data.get("school")

        if not school_uuid:
            return None

        return school_uuid

    @property
    def requested_classroom_uuid(self):
        return self.kwargs.get("classroom_uuid")

    def create(self, request, *args, **kwargs):
        """
        Creating a classroom also triggers the creation of an enrollment for the teacher
        """

        classroom_serializer = self.serializer_class(data=request.data)
        classroom_serializer.is_valid(raise_exception=True)
        classroom_serializer.save()

        enrollment_data = {
            "classroom_instance": classroom_serializer.data["uuid"],
            "user_id": request.user.email,
            "staff": True,
        }

        enrollment_serializer = self.enrollment_serializer_class(data=enrollment_data)
        enrollment_serializer.is_valid(raise_exception=True)
        enrollment_serializer.save()

        return Response(
            {
                **classroom_serializer.data,
                "classroom_uuid": enrollment_serializer.data["classroom_uuid"],
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """
        Update a classroom data.

        The 'school' may not be specified via the HTTP API since it can only be
        assigned when the classroom is created.
        """
        classroom = get_object_or_404(Classroom, uuid=kwargs.get("classroom_uuid"))

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

        serializer = self.serializer_class(instance=classroom, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Disable DELETE because all classromms should be kept and deactivated to be
        archived.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        """
        Disable PATCH because all classroom modifications should done with the UPDATE
        endpoint.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_permission_object(self):
        """
        Retrieves the apporpriate user object to use during edx-rbac's permission checks.
        This object is passed to the rule predicate(s).

        The requesting user needs to be part of a school to have access to the classroom
        feature.
        """
        return self.requested_school_uuid

    @action(detail=True, methods=["post"])
    def enroll(self, request, classroom_uuid):
        """Create enrollment(s) for one or more users"""

        identifiers_raw = request.data.get("identifiers")
        identifiers = self._split_input_list(identifiers_raw)
        for identifier in identifiers:
            # TODO validate the users are part of the same enterprise
            enrollment_data = {
                "classroom_instance": classroom_uuid,
                "user_id": identifier,
            }

            enrollment_serializer = self.enrollment_serializer_class(
                data=enrollment_data
            )
            enrollment_serializer.is_valid(raise_exception=True)
            enrollment_serializer.save()

        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def courses(self, request, classroom_uuid):
        """Get the list of courses"""

        course_list = get_course_list()

        return Response(status=status.HTTP_200_OK, data=course_list)


class ClassroomEnrollmentViewSet(viewsets.ModelViewSet):
    """
    Viewset for operations on classroom enrollments
        - List enrollments for the current classroom (GET enrollments/)
        - retrieve single enrollment (GET enrollments/<id>)
        - TODO Update
        - TODO Delete

    Viewset for operations on individual enrollments in a given classroom.
    """

    authentication_classes = [JwtAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    lookup_fields = "classroom_uuid"
    lookup_url_kwarg = "id"
    # lookup_field = "user_id"

    serializer_class = ClassroomEnrollmentSerializer

    def _get_classroom(self):
        """
        Helper that returns the classroom specified by `classroom_uuid` in the request.
        """
        classroom_uuid = self.kwargs.get("classroom_uuid")

        if not classroom_uuid:
            return None

        try:
            return Classroom.objects.get(uuid=classroom_uuid)
        except Classroom.DoesNotExist:
            return None

    def get_queryset(self):
        queryset = ClassroomEnrollment.objects.filter(
            classroom_instance=self._get_classroom()
        )

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a classroom enrollment
        Parameters:
            - user_id: ID of the user enrolled in the Classroom
        """
        enrollment_data = {
            "classroom_instance": self._get_classroom().uuid,
            "user_id": self.request.data.get("user_id"),
        }

        enrollment = self.serializer_class(data=enrollment_data)
        enrollment.is_valid(raise_exception=True)
        enrollment.save()

        return Response(
            data=enrollment.data,
            status=status.HTTP_201_CREATED,
        )

    # def retrieve(self, request, user_id):

    #     enrollment_data = {
    #         "classroom_instance": self._get_classroom().uuid,
    #         "user_id": user_id,
    #     }

    #     serializer = self.serializer_class(data=enrollment_data)

    #     return serializer

    def update(self, request, *args, **kwargs):
        """
        Disable UPDATE because enrollments cannot be amended.
        """
        return Response(status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        """
        Disable PATCH because enrollments cannot be amended.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CourseAssignmentViewset(viewsets.ModelViewSet):
    """
    Viewset for operations on course assignments

    """

    authentication_classes = [JwtAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    lookup_fields = "classroom_uuid"
    lookup_url_kwarg = "course_id"

    serializer_class = CourseAssignmentSerializer

    def _get_classroom(self):
        """
        Helper that returns the classroom specified by `classroom_uuid` in the request.
        """
        classroom_uuid = self.kwargs.get("classroom_uuid")

        if not classroom_uuid:
            return None

        try:
            return Classroom.objects.get(uuid=classroom_uuid)
        except Classroom.DoesNotExist:
            return None

    def get_queryset(self):
        queryset = CourseAssignment.objects.filter(
            classroom_instance=self._get_classroom()
        )

        return queryset

    def destroy(self, request, *args, **kwargs):
        """
        Disable DELETE for now.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        """
        Disable PATCH for now.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
