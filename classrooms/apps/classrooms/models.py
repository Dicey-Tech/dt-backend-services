"""
Database models for classroom.
"""
from uuid import uuid4
from datetime import date, datetime, timedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _

from edx_rbac.models import UserRole, UserRoleAssignment
from edx_rbac.utils import ALL_ACCESS_CONTEXT

from model_utils.models import TimeStampedModel

from classrooms.apps.api_client.discovery import DiscoveryApiClient
from classrooms.apps.classrooms.constants import DATE_FORMAT, DATETIME_FORMAT


class Classroom(TimeStampedModel):
    """
    A Classroom is an entity grouping learners, teachers and courses automating
    the enrollment.

    Fields:
        uuid (UUIDField, PRIMARY KEY): Classroom Instance identification code.
        school (UUIDField): Enterprise identification code.
        name (CharField): Display name of the Classroom.
        active (BooleanField):
    """

    class Meta:
        app_label = "classrooms"
        verbose_name = _("Classroom")
        verbose_name_plural = _("Classrooms")
        ordering = ["created"]

    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    school = models.UUIDField(null=False, help_text=_("School uuid."))
    name = models.CharField(
        max_length=255,
        blank=False,
        default="Your Classroom Name",
        help_text=_("Specifies the displayed name of the classroom"),
    )
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        """
        Return a human-readable string representation.
        """
        return f"<ClassroomInstance {self.name} with ID {self.uuid}>"

    def __repr__(self) -> str:
        """
        Return uniquely identifying string representation
        """
        return self.__str__()


class ClassroomEnrollment(TimeStampedModel):
    """
    Store infromation about the enrollment of a user in a classroom.

    Fields:
        classroom_instance (ForeignKey): Classroom Instance identification code.
        user_id (PositiveIntegerField)
        active (BooleanField)
    """

    class Meta:
        unique_together = (("classroom_instance", "user_id"),)
        app_label = "classrooms"
        ordering = ["created"]

    classroom_instance = models.ForeignKey(
        Classroom,
        blank=False,
        null=False,
        on_delete=models.deletion.CASCADE,
        help_text=_("The classroom to which this enrollment is attached"),
    )

    user_id = models.EmailField(
        blank=False,
        null=False,
        max_length=254,
        db_index=True,
        help_text=_("User identifier"),
    )

    staff = models.BooleanField(default=False)

    def __str__(self) -> str:
        """
        Return a human-readable string representation.
        """
        return f"<ClassroomEnrollment for user {self.user_id} in classroom with ID {self.classroom_instance.uuid}>"

    def __repr__(self):
        """
        Return string representation of the enrollment.
        """
        return self.__str__()


class CourseAssignment(TimeStampedModel):
    """
    CourseAssignment links courses with a specific classroom.

    Fields:
        course_id (CharField):
        classroom_instance (ForeignKey):

    """

    class Meta:
        unique_together = (("classroom_instance", "course_id"),)
        app_label = "classrooms"
        ordering = ["created"]

    course_id = models.CharField(
        max_length=255,
        blank=False,
        help_text=_("Unique identifier for the course"),
    )

    classroom_instance = models.ForeignKey(
        Classroom,
        blank=True,
        null=True,
        on_delete=models.deletion.CASCADE,
        help_text=_("The classroom to which this assignment is attached"),
    )

    def __str__(self) -> str:
        """
        Return a human-readable string representation.
        """
        return f"<CourseAssignment for course {self.course_id} in classroom with ID {self.classroom_instance.uuid}>"

    def __repr__(self):
        """
        Return string representation of the enrollment.
        """
        return self.__str__()

    def save(self, *args, **kwargs):
        """
        Create a new course run from the course ID selected and assign the new course to the
        classroom.
        """

        course_run = (
            self.classroom_instance.name.replace(" ", "")
            + "_"
            + date.today().strftime(DATE_FORMAT)
        )

        # Create a course run using the discovery API DiceyTech+DT002
        course_key = self.course_id.replace("+TEMPLATE", "")
        start = datetime.today()
        end = start + timedelta(days=90)

        client = DiscoveryApiClient()

        run_type = client.get_course_run_type(course_key)

        course_data = {
            "start": start.strftime(DATETIME_FORMAT),
            "end": end.strftime(DATETIME_FORMAT),
            "pacing_type": "self_paced",
            "run_type": run_type,
            "status": "published",
            "course": course_key,
            "term": course_run,
        }

        response = client.create_course_run(course_data)

        self.course_id = self.course_id.replace("TEMPLATE", course_run)

        super().save(*args, **kwargs)


class ClassroomFeatureRole(UserRole):
    """
    User role definitions specific to classrooms.
     .. no_pii:
    """

    def __str__(self):
        """
        Return human-readable string representation.
        """
        return f"ClassroomFeatureRole(name={self.name})"

    def __repr__(self):
        """
        Return uniquely identifying string representation.
        """
        return self.__str__()


class ClassroomRoleAssignment(UserRoleAssignment):
    """
    Model to map users to a ClassroomFeatureRole.
     .. no_pii:
    """

    role_class = ClassroomFeatureRole
    enterprise_customer_uuid = models.UUIDField(
        blank=True, null=True, verbose_name="Enterprise Customer UUID"
    )

    def get_context(self):
        """
        Return the enterprise customer id or `*` if the user has access to all resources.
        """
        if self.enterprise_customer_uuid:
            return str(self.enterprise_customer_uuid)
        return ALL_ACCESS_CONTEXT

    @classmethod
    def user_assignments_for_role_name(cls, user, role_name):
        """
        Returns assignments for a given user and role name.
        """
        return cls.objects.filter(user__id=user.id, role__name=role_name)

    def __str__(self):
        """
        Return human-readable string representation.
        """
        return "ClassroomRoleAssignment(name={name}, user={user})".format(
            name=self.role.name,  # pylint: disable=no-member
            user=self.user.id,
        )

    def __repr__(self):
        """
        Return uniquely identifying string representation.
        """
        return self.__str__()
