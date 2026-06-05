from rest_framework.viewsets import ModelViewSet
from config.permissions import IsAdminOrReadOnly
from branches.models import Branch, Subject, Group
from .serializers import BranchSerializer, SubjectSerializer, GroupSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(tags=['Branches']),
    retrieve=extend_schema(tags=['Branches']),
    create=extend_schema(tags=['Branches']),
    update=extend_schema(tags=['Branches']),
    partial_update=extend_schema(tags=['Branches']),
    destroy=extend_schema(tags=['Branches']),
)

class BranchViewSet(ModelViewSet):

    serializer_class = BranchSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = ["status", "city"]
    search_fields = ["name"]

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Branch.objects.none()

        return self.request.user.get_visible_branches()

@extend_schema(tags=['Subjects'])
class SubjectViewSet(ModelViewSet):

    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = ["status", "branch"]
    search_fields = ["name"]

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Subject.objects.none()

        return Subject.objects.filter(
            branch__in=self.request.user.get_visible_branches()
        )

@extend_schema(tags=['Groups'])
class GroupViewSet(ModelViewSet):

    serializer_class = GroupSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = ["status", "branch"]
    search_fields = ["name"]

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Group.objects.none()

        return Group.objects.filter(
            branch__in=self.request.user.get_visible_branches()
        )