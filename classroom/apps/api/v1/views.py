"""
Viewsets
"""

from rest_framework import viewsets

from classroom.apps.api.serializers import (
    ClassroomSerializer,
)
from classroom.apps.classroom.models import ClassroomInstance


class ClassroomCRUDViewSet(viewsets.ModelViewSet):
    """ Viewset for CRUD operations on Classrooms """

    serializer_class = ClassroomSerializer
    queryset = ClassroomInstance.objects.all()
