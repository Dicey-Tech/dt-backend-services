"""
Database models for classroom.
"""
from uuid import uuid4

from django.db import models
from django.utils.translation import ugettext_lazy as _
from enterprise.models import EnterpriseCustomer, EnterpriseCustomerUser

from model_utils.models import TimeStampedModel

# TODO should I use the REST API or the python API?
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
    name = models.CharField(
        max_length=25,
        blank=False,
        help_text=_("Specifies the displayed name of the classroom."),
    )
    school = models.ForeignKey(
        EnterpriseCustomer,
        blank=False,
        null=False,
        related_name="enterprise_customer_classroom",
        on_delete=models.deletion.CASCADE,
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

    user = models.ForeignKey(
        EnterpriseCustomerUser, null=False, on_delete=models.deletion.CASCADE
    )
    role = models.CharField(
        max_length=25,
        blank=False,
        help_text=_("Specifies role of the enrolled user customer type."),
    )

    def __str__(self):
        """
        Create string representation of the enrollment.
        """
        return "<PendingEnrollment for email {} in course with ID {}>".format(
            self.user.user_email, self.course_id
        )

    def __repr__(self):
        """
        Return string representation of the enrollment.
        """
        return self.__str__()