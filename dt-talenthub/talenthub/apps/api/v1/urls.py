"""
API v1 URLs.

/api/v1/demographics/
/api/v1/demographics/{user_id}
"""
from rest_framework_nested import routers
from talenthub.apps.api.v1 import views

app_name = "v1"

router = routers.DefaultRouter()
router.register(r"demographics", views.DemographicsViewset, basename="demographics")

urlpatterns = router.urls
