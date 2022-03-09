""" 
API v1 URLs. 

The use of `NestedSimpleRouter` below allows us to defined
nested routes backed by the `ClassroomsViewSet`.  That is:

/api/v1/classrooms/{classrooms_uuid}/enrollments/
/api/v1/classrooms/{classrooms_uuid}/enrollments/{enrollments_uuid}/
"""
from rest_framework_nested import routers

from learninghub.apps.api.v1 import views


app_name = "v1"


class NestedMixin(routers.NestedMixin):
    """
    This is a hack to work around a shortcoming of the rest_framework_nested
    `NestedMixin` class: https://github.com/alanjds/drf-nested-routers/issues/147

    Without this trickery, you can't tell `NestedMixin` to just use
    the `lookup_field` or `lookup_url_kwarg` of the router's viewset as the
    lookup URL kwarg of a nested router - it will *always* try to build its
    own, non-empty default if not provided, and will insist on appending a "_"
    if you provide a non-empty value.  The properties below trick this base
    class's __init__() method into not doing anything during mutation,
    but returning an empty string when `nest_prefix` is read.  The `nest_prefix`
    is used as a prefix of either the ViewSets `lookup_url` or `lookup_url_kwarg`
    field when building the lookup regular expression's name.
    """

    @property
    def nest_prefix(self):
        return ""

    @nest_prefix.setter
    def nest_prefix(self, value):
        pass

    def check_valid_name(self, value):
        return True


class NestedDefaultRouter(NestedMixin, routers.DefaultRouter):
    """
    Same as `rest_framework_nested.routers.DefaultRouter`, only
    with the custom `NestedMixin` defined above.
    """


router = routers.DefaultRouter()
router.register(r"classrooms", views.ClassroomsViewSet, basename="classrooms")
# router.register(
#     r"enrollments",
#     views.ClassroomEnrollmentViewSet,
#     basename="enrollments",
# )

classroom_router = NestedDefaultRouter(
    parent_router=router,
    parent_prefix="classrooms",
)
classroom_router.register(
    r"enrollments",
    views.ClassroomEnrollmentViewSet,
    basename="enrollments",
)

classroom_router.register(
    r"assignments",
    views.CourseAssignmentViewset,
    basename="assignments",
)

urlpatterns = []

urlpatterns += router.urls
urlpatterns += classroom_router.urls
