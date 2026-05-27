from rest_framework.routers import DefaultRouter
from .views import LessonViewSet, AttendanceViewSet, LessonTemplateViewSet

router = DefaultRouter()

router.register("lessons", LessonViewSet, basename="api-lessons")
router.register("attendance", AttendanceViewSet, basename="api-attendance")
router.register("lesson-templates", LessonTemplateViewSet, basename="api-lesson-templates")

urlpatterns = router.urls