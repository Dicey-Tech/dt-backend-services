"""
Serializers for REST API endpoints
"""
from rest_framework import serializers
from talenthub.apps.demographics.models import UserDemographics


class DemographicsSerializer(serializers.ModelSerializer):
    """Serializes the UserDemographics object."""

    class Meta:
        model = UserDemographics
        fields = ["user", "gender", "user_ethnicity", "education_level"]
        lookup_field = "user"
