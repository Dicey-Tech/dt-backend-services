"""
Views for classroom end points.
"""

import logging
import re
from typing import List

from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from edx_rbac.mixins import PermissionRequiredForListingMixin
from edx_api_doc_tools import (
    schema_for,
    query_parameter,
)

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
from classrooms.apps.classrooms.course_list import get_course_list

logger = logging.getLogger(__name__)


@schema_for(
    "list",
    """
    Fetch the list of classrooms the request user is enrolled in.
    """,
)
@schema_for(
    "retrieve",
    """
    Fetch details for a single classroom by uuid.
    """,
)
@schema_for(
    "create",
    """
    Create a classroom.

    Creating a classroom also triggers the creation of an enrollment for the as staff for 
    the user initiating the call.
    """,
)
@schema_for(
    "update",
    """
    Edit a classroom name or status.

    The 'school' may not be specified via the HTTP API since it can only be
    assigned when the classroom is created.
    """,
)
@schema_for(
    "courses",
    """
    Get the list of course IDs that can be used to create course assignments.
    """,
    responses={
        200: """
        [{
            "key": "course-v1:DiceyTech+EXP001+TEMPLATE",
            "uuid": "ee27844d-fd85-46eb-ae6a-fff649094ab1",
            "title": "RPS",
            "external_key": null,
            "image": {
            "src": "http://local.overhang.io/asset-v1:DiceyTech+EXP001+TEMPLATE+type@asset+block@Rock_Paper_Scissors_Project_Cover.png",
            "description": null,
            "height": null,
            "width": null
            },
            "short_description": null,
            "marketing_url": "course/rps-course-v1diceytechexp001template?utm_source=sofiane&utm_medium=affiliate_partner",
            "seats": [
                {
                    "type": "honor",
                    "price": "0.00",
                    "currency": "USD",
                    "upgrade_deadline": null,
                    "credit_provider": null,
                    "credit_hours": null,
                    "sku": "A947FB2",
                    "bulk_sku": null
                }
            ],
            "start": "2030-01-01T00:00:00Z",
            "end": null,
            "go_live_date": null,
            "enrollment_start": null,
            "enrollment_end": null,
            "pacing_type": "instructor_paced",
            "type": "honor",
            "run_type": "1cfaba8e-16c2-4342-addd-4937b38c05ce",
            "status": "published",
            "is_enrollable": true,
            "is_marketable": true,
            "course": "DiceyTech+EXP001",
            "full_description": null,
            "announcement": null,
            "video": null,
            "content_language": null,
            "license": "",
            "outcome": null,
            "transcript_languages": [],
            "instructors": [],
            "staff": [],
            "min_effort": null,
            "max_effort": null,
            "weeks_to_complete": null,
            "modified": "2021-09-27T10:41:55.233173Z",
            "level_type": null,
            "availability": "Upcoming",
            "mobile_available": false,
            "hidden": false,
            "reporting_type": "mooc",
            "eligible_for_financial_aid": true,
            "first_enrollable_paid_seat_price": null,
            "has_ofac_restrictions": null,
            "ofac_comment": "",
            "enrollment_count": 0,
            "recent_enrollment_count": 0,
            "expected_program_type": null,
            "expected_program_name": "",
            "course_uuid": "17df0b65-c588-4608-9edc-1fa3fdbcc2d6",
            "estimated_hours": 0,
            "content_language_search_facet_name": null
        }]
        """,
    },
)
# TODO Improve Parameter display
@schema_for(
    "enroll",
    """
    Create enrollment(s) for one or more users.

    **Example Request**

        POST api/v1/classrooms/<uuid>/enroll/ {
            'identifiers': 'student_1@school.sch,student2@school.sch',
        }
    """,
    # parameters=[
    #     string_parameter(
    #         "identifiers",
    #         ParameterLocation.BODY,
    #         "A string of email that can be separated by a new line, a comma or a space",
    #     ),
    # ],
    responses={
        201: "Response body is currently empty.",
    },
)
class ClassroomsViewSet(PermissionRequiredForListingMixin, viewsets.ModelViewSet):
    """
    Viewset for CRUD operations on Classroom models.
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

    def _split_input_list(self, str_list: str) -> List:
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
    def requested_school_uuid(self) -> str:
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
    def requested_classroom_uuid(self) -> str:
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

    def update(self, request, *args, **kwargs) -> Response:
        """
        Update a classroom name or status.
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

    def destroy(self, request, *args, **kwargs) -> Response:
        """
        ** Not allowed. **

        Disable DELETE because all classromms should be kept and deactivated to be
        archived.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs) -> Response:
        """
        ** Not allowed. **

        Disable PATCH because all classroom modifications should done with the UPDATE
        endpoint.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_permission_object(self) -> str:
        """
        Retrieves the apporpriate user object to use during edx-rbac's permission checks.
        This object is passed to the rule predicate(s).

        The requesting user needs to be part of a school to have access to the classroom
        feature.
        """
        return self.requested_school_uuid

    @action(detail=True, methods=["post"])
    def enroll(self, request, classroom_uuid: str) -> Response:
        """
        Create enrollment(s) for one or more users.

        TODO: Response body is currently empty.
        TODO: Enroll additional staff
        """

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
    def courses(self, request, classroom_uuid: str) -> Response:
        """
        ** Get the list of course IDs that can be used to create course assignments. **

        If an error occur an empty list will be returned.

        **Example Request**

            GET api/v1/classrooms/<uuid>/courses

        **Response Values**

            Reponse.data = [
                "course-v1:DiceyTech+EXP001+TEMPLATE",
                "course-v1:DiceyTech+EXP002+TEMPLATE"
            ]

        """

        course_list = get_course_list(classroom_uuid)

        return Response(status=status.HTTP_200_OK, data=course_list)


@schema_for(
    "list",
    """
    Get the list of all enrollments linked to this classroom.
    """,
)
@schema_for(
    "retrieve",
    """
    Fetch details for a single classroom enrollment by id.
    """,
    parameters=[query_parameter("id", int, "Enrollment id")],
)
# TODO Improve Parameter display
@schema_for(
    "create",
    """
    Create a classroom enrollment.

    **POST Parameters**

        A POST request must include an emails.

        * user_id: ID of the user enrolled in the Classroom
    """,
)
class ClassroomEnrollmentViewSet(viewsets.ModelViewSet):
    """
    Viewset for CRUD operations on ClassroomEnrollment models.
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
        """Create a classroom enrollment"""
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

    # def retrieve(self, request, *args, **kwargs):
    #     enrollment_data = {
    #         "classroom_instance": self._get_classroom().uuid,
    #         "user_id": user_id,
    #     }

    #     serializer = self.serializer_class(data=enrollment_data)

    #     return serializer
    def destroy(self, request, *args, **kwargs):
        """
        ** Not allowed. **

        Disable for now until unenrollment is implemented.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        """
        ** Not allowed. **

        Enrollments cannot be amended.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        """
        ** Not allowed **

        Enrollments cannot be amended.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@schema_for(
    "list",
    """
    Get the list of all assignments linked to this classroom.
    """,
)
@schema_for(
    "retrieve",
    """
    Fetch details for a single classroom assignent by id.
    """,
    # parameters=[query_parameter("id", int, "Enrollment id")],
)
# TODO Improve Parameter display
@schema_for(
    "create",
    """
    Create a course assignment.
    """,
)
class CourseAssignmentViewset(viewsets.ModelViewSet):
    """Viewset for operations on course assignments"""

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

    def update(self, request, *args, **kwargs):
        """
        ** Not allowed **

        Course assignments cannot be amended.

        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        """
        ** Not allowed **

        For now until unenrollment is implemented.

        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        """
        ** Not allowed **

        Course assignments cannot be amended.

        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
