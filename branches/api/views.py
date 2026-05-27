from rest_framework.viewsets import ModelViewSet

from config.permissions import IsAdminOrReadOnly

from branches.models import (
    Branch,
    Subject,
    Group,
)

from .serializers import (
    BranchSerializer,
    SubjectSerializer,
    GroupSerializer,
)


class BranchViewSet(ModelViewSet):

    serializer_class = BranchSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = ["status", "city"]
    search_fields = ["name"]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Branch.objects.none()
        return self.request.user.get_visible_branches()


class SubjectViewSet(ModelViewSet):

    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = ["status", "branch"]
    search_fields = ["name"]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Subject.objects.none()
        return Subject.objects.filter(
            branch__in=self.request.user.get_visible_branches()
        )


class GroupViewSet(ModelViewSet):

    serializer_class = GroupSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = ["status", "branch"]
    search_fields = ["name"]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Group.objects.none()
        return Group.objects.filter(
            branch__in=self.request.user.get_visible_branches()
        )