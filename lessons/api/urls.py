from rest_framework.routers import DefaultRouter

from .views import (
    LessonViewSet,
    AttendanceViewSet,
)

router = DefaultRouter()

router.register("lessons", LessonViewSet, basename="api-lessons")
router.register("attendance", AttendanceViewSet, basename="api-attendance")

urlpatterns = router.urls