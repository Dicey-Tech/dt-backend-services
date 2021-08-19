"""
Database models for classroom.
"""
from uuid import uuid4

from django.db import models
from django.utils.translation import ugettext_lazy as _

from edx_rbac.models import UserRole, UserRoleAssignment
from edx_rbac.utils import ALL_ACCESS_CONTEXT

from model_utils.models import TimeStampedModel


class Classroom(TimeStampedModel):
    """
    A Classroom is an entity grouping learners, teachers and courses automating
    the enrollment.

    Fields:
        uuid (UUIDField, PRIMARY KEY): Classroom Instance identification code.
        school
        name
        active
    """

    class Meta:
        app_label = "classroom"
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


class ClassroomEnrollement(TimeStampedModel):
    """
    Store infromation about the enrollment of a user in a classroom.

    Fields:
        classroom_id (UUIDField, PRIMARY KEY): Classroom Instance identification code.
        user_id
        active
    """

    class Meta:
        unique_together = (("classroom_instance", "user_id"),)
        app_label = "classroom"
        ordering = ["created"]

    classroom_instance = models.ForeignKey(
        Classroom,
        blank=True,
        null=True,
        related_name="classroom",
        related_query_name="classroom",
        on_delete=models.deletion.CASCADE,
        help_text=_("The classroom to which this enrollment is attached"),
    )

    user_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        db_index=True,
    )

    active = models.BooleanField(default=True)

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
