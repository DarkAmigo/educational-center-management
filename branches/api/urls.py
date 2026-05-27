from rest_framework.routers import DefaultRouter

from .views import (
    BranchViewSet,
    SubjectViewSet,
    GroupViewSet,
)

router = DefaultRouter()

router.register("branches", BranchViewSet, basename="api-branches")
router.register("subjects", SubjectViewSet, basename="api-subjects")
router.register("groups", GroupViewSet, basename="api-groups")

urlpatterns = router.urls