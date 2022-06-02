"""
Views for talenthub API.
"""

import logging

from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from talenthub.apps.api.serializers import DemographicsSerializer
from talenthub.apps.demographics.models import UserDemographics

logger = logging.getLogger(__name__)


class DemographicsViewset(viewsets.ModelViewSet):
    """
    Views for CRUD operations on Demographic
    """

    permission_classes = [permissions.IsAuthenticated]

    lookup_field = "user"
    lookup_url_kwarg = "user"

    queryset = UserDemographics.objects.all()
    serializer_class = DemographicsSerializer

    def get_queryset(self):
        """ """
        user_id = (
            self.kwargs.get("user") if self.kwargs.get("user") else self.request.user.id
        )

        if self.request.user.is_staff or self.request.user.is_superuser:
            return UserDemographics.objects.all()
        else:
            return UserDemographics.objects.filter(user=user_id)

    def create(self, request, *args, **kwargs) -> Response:
        """Create a demographic profile"""

        demographics_data = {
            "user": request.data.get("user"),
            "gender": request.data.get("gender"),
            "user_ethnicity": request.data.get("user_ethnicity")
            if request.data.get("user_ethnicity")
            else "",
            "education_level": request.data.get("learner_education_level"),
        }

        try:
            demographics_serializer = self.serializer_class(data=demographics_data)
            demographics_serializer.is_valid(raise_exception=True)
            demographics_serializer.save()

            return Response(status=status.HTTP_201_CREATED)
        except ValidationError as exc:
            # Handles calls attempting to create a profile when the
            # user profile already exists
            error_message = str(exc.detail.get("user")[0])

            return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs) -> Response:
        """
        ** Not allowed **

        Disable DELETE for now.
        """

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
