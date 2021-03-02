"""
Database models for classroom.
"""
from uuid import uuid4
from logging import getLogger

from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

LOGGER = getLogger(__name__)


class Classroom(TimeStampedModel):
    """
    Classroom

    """

    class Meta:
        app_label = "classroom"
        verbose_name = _("Classroom")
        verbose_name_plural = _("Classrooms")
        ordering = ["name"]

    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    school = models.UUIDField(
        null=False,
        help_text=_("Enterprise Customer code."),
    )

    name = models.CharField(
        max_length=25,
        blank=False,
        help_text=_("Specifies the displayed name of the classroom."),
    )

    def __str__(self):
        """
        Return human-readable string representation.
        """
        return self.name

    def __repr__(self):
        """
        Return uniquely identifying string representation.
        """
        return self.__str__()


class ClassroomEnrollment(TimeStampedModel):
    """
    ClassroomEnrollment
    """

    class Meta:
        app_label = "classroom"
        unique_together = (("classroom", "user_id"),)

    classroom = models.ForeignKey(
        Classroom,
        blank=False,
        null=False,
        related_name="enterprise_customer_users",
        on_delete=models.deletion.CASCADE,
    )
    user_id = models.PositiveIntegerField(null=False, blank=False)
    role = models.CharField(
        max_length=25,
        blank=False,
        help_text=_("Specifies role of the enrolled user Student or Teacher."),
    )

    def __str__(self):
        """
        Return human-readable string representation.
        """
        return self.user_id

    def __repr__(self):
        """
        Return uniquely identifying string representation.
        """
        return self.__str__()
