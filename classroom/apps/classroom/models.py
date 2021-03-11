"""
Database models for classroom.
"""
from uuid import uuid4

from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel


class ClassroomInstance(TimeStampedModel):
    """
    A Classroom is an entity grouping learners, teachers and courses automating
    the enrollment.

    Fields:
        uuid (UUIDField, PRIMARY KEY): Classroom Instance code - used
            other parts of the system (SSO, ecommerce, analytics etc.).
    """

    class Meta:
        app_label = "classroom"
        verbose_name = _("Classroom")
        verbose_name_plural = _("Classrooms")
        ordering = ["created"]

    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    school = models.UUIDField(null=False, help_text=_("School uuid."))
    name = models.CharField(
        max_length=140,
        blank=False,
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
    """

    class Meta:
        unique_together = (("classroom_instance_id", "user_id"),)
        app_label = "classroom"
        ordering = ["created"]

    classroom_instance_id = models.ForeignKey(
        ClassroomInstance,
        blank=True,
        null=True,
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
        return f"<ClassroomEnrollment for user {self.user_id} in course with ID {self.classroom_instance_id}>"

    def __repr__(self):
        """
        Return string representation of the enrollment.
        """
        return self.__str__()