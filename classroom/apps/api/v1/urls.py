""" API v1 URLs. """
from rest_framework.routers import DefaultRouter
from classroom.apps.api.v1 import views


app_name = "v1"

router = DefaultRouter()
router.register(r"classrooms", views.ClassroomsViewSet, basename="classroom")
router.register(
    r"classroom-enrollments",
    views.ClassroomEnrollmentViewSet,
    basename="enrollments",
)

urlpatterns = []

urlpatterns += router.urls
