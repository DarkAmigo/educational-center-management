from rest_framework.routers import DefaultRouter

from .views import StudentViewSet

router = DefaultRouter()

router.register("", StudentViewSet, basename="api-students")

urlpatterns = router.urls