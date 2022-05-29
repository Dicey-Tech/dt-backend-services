"""
Database models for demographics.
"""

import logging

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_noop
from model_utils.models import TimeStampedModel

logger = logging.getLogger(__name__)


class UserDemographics(TimeStampedModel):
    """Demographic user profile.
    This model used to store user identity, education and socio-economic information.

    Fields:
        user (PositiveIntegerField, PRIMARY KEY): LMS User ID.
        gender (Charfield): User gender.
        user_ethnicity (Charfield): User ethnicity.
        education_level (Charfield): User education level.
    """

    class Meta:
        app_label = "demographics"
        verbose_name = _("User Demographic")
        verbose_name_plural = _("User Demographic")
        ordering = ["created"]

    user = models.PositiveIntegerField(primary_key=True, editable=True)

    class GenderChoices(models.TextChoices):
        MALE = "m", gettext_noop("Male")
        FEMALE = "f", gettext_noop("Female")
        TRANS = "t", gettext_noop("Transgender")
        OTHER = "o", gettext_noop("Other/Prefer Not to Say")

    gender = models.CharField(
        blank=True,
        null=True,
        db_index=True,
        max_length=6,
        choices=GenderChoices.choices,
    )

    class EthnicityChoices(models.TextChoices):
        ASIAN_EAST = "ea", gettext_noop("East - Asian")
        ASIAN_SOUTHWEST = "as", gettext_noop("Southwest - Asian")
        BLACK_AFRICAN = "ba", gettext_noop("Black - African")
        BLACK_CARIBBEAN = "bc", gettext_noop("Black - Caribbean")
        BLACK_EUROPEAN = "be", gettext_noop("Black - European")
        MIDDLE_EASTERN = "me", gettext_noop("Middle Eastern")
        WHITE_AMERICAN = "wa", gettext_noop("White - American")
        WHITE_EUROPEAN = "we", gettext_noop("White - European")

    user_ethnicity = models.CharField(
        blank=True,
        null=True,
        max_length=6,
        db_index=True,
        choices=EthnicityChoices.choices,
    )

    class EducationLevelChoices(models.TextChoices):
        DOCTORATE = "p", gettext_noop("Doctorate")
        MASTERS = "m", gettext_noop("Master's or professional degree")
        BACHELORS = "b", gettext_noop("Bachelor's degree")
        SECONDARY = "hs", gettext_noop("Secondary/high school")
        PRIMARY = "el", gettext_noop("Elementary/primary school")
        APPRENTICE = "ap", gettext_noop("Apprentice")
        NONE = "none", gettext_noop("No formal education")
        OTHER = "other", gettext_noop("Other education")

    education_level = models.CharField(
        blank=True, null=True, max_length=6, choices=EducationLevelChoices.choices
    )

    def __str__(self) -> str:
        """
        Return a human-readable string representation.
        """
        return f"<UserDemographics for user with ID {self.user}>"

    def __repr__(self) -> str:
        """
        Return uniquely identifying string representation
        """
        return self.__str__()
