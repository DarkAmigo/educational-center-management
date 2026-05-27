from rest_framework.viewsets import ModelViewSet

from users.models import User

from lessons.models import (
    Lesson,
    Attendance,
)

from config.permissions import IsAdminOrReadOnly

from .serializers import (
    LessonSerializer,
    AttendanceSerializer,
)

from drf_spectacular.utils import extend_schema

@extend_schema(
    summary="Create lesson",
    description="Creates a lesson with conflict detection"
)

class LessonViewSet(ModelViewSet):

    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = [
        "teacher",
        "subject",
        "status",
    ]

    ordering_fields = [
        "start_datetime",
    ]

    def get_queryset(self):

        user = self.request.user

        if not user.is_authenticated:
            return Lesson.objects.none()

        lessons = Lesson.objects.select_related(
            "teacher",
            "student",
            "group",
            "subject",
        )

        if user.role == User.Role.TEACHER:
            return lessons.filter(teacher=user)

        return lessons.filter(
            subject__branch__in=user.get_visible_branches()
        )


class AttendanceViewSet(ModelViewSet):

    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = [
        "lesson",
        "student",
        "status",
    ]

    def get_queryset(self):

        user = self.request.user

        if not user.is_authenticated:
            return Attendance.objects.none()

        attendance = Attendance.objects.select_related(
            "lesson",
            "student",
        )

        if user.role == User.Role.TEACHER:
            return attendance.filter(
                lesson__teacher=user
            )

        return attendance.filter(
            lesson__subject__branch__in=user.get_visible_branches()
        )