from django.db.models import Q

from rest_framework.viewsets import ModelViewSet

from users.models import User
from students.models import Student

from config.permissions import IsAdminOrReadOnly

from .serializers import StudentSerializer


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

        user = self.request.user
        
        if not user.is_authenticated:
            return Student.objects.none()

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