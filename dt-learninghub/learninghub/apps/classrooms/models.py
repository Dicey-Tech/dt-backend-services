"""
Database models for classroom.
"""
import logging
from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _
from edx_rbac.models import UserRole, UserRoleAssignment
from edx_rbac.utils import ALL_ACCESS_CONTEXT
from learninghub.apps.classrooms.course_runs import create_course_run
from model_utils.models import TimeStampedModel

logger = logging.getLogger(__name__)


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
    # TODO Is it worth using StatusModel for auditing?
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
    # TODO Add TimeFramedModel to allow editing of start and end dates for assignments
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
        # TODO Check if course run exist

        # If the assignment already exist just update it
        if self.pk is not None:
            super().save(*args, **kwargs)
            return

        self.course_id = create_course_run(self.course_id)

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
