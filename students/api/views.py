from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view 
from users.models import User
from students.models import Student
from config.permissions import IsAdminOrReadOnly
from .serializers import StudentSerializer

@extend_schema(tags=["Students"]) 
@extend_schema_view(
    list=extend_schema(summary="List students", description="Get students filtered by permissions"),
    create=extend_schema(summary="Create student"),
    retrieve=extend_schema(summary="Get student details"),
    update=extend_schema(summary="Update student"),
    partial_update=extend_schema(summary="Partially update student"),
    destroy=extend_schema(summary="Delete student"),
)
class StudentViewSet(ModelViewSet):
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = ["branch", "status"]

    search_fields = [
        "first_name",
        "last_name",
        "phone",
    ]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Student.objects.none()

        user = self.request.user
        students = Student.objects.select_related("branch")

        if user.role == User.Role.ADMIN:
            if user.is_superuser:
                return students

            return students.filter(
                branch__in=user.get_visible_branches()
            )

        return students.filter(
            Q(lessons__teacher=user) |
            Q(memberships__group__lessons__teacher=user)
        ).distinct()