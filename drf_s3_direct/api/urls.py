from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(
    prefix="",
    viewset=views.S3FileView,
    basename="drf-s3-direct",
)
urlpatterns = router.urls
