""" API v1 URLs. """
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from classroom.apps.api.v1 import views


app_name = "v1"

router = DefaultRouter()
router.register(r"classroom", views.ClassroomCRUDViewSet, basename="classroom")

urlpatterns = []

urlpatterns += router.urls
