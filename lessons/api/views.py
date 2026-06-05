from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema, extend_schema_view 
from users.models import User
from lessons.models import Lesson, Attendance, LessonTemplate
from config.permissions import IsAdminOrReadOnly, CanManageAttendance
from .serializers import LessonSerializer, AttendanceSerializer, LessonTemplateSerializer

@extend_schema(tags=["Lessons"])
@extend_schema_view(
    list=extend_schema(summary="List lessons"),
    create=extend_schema(summary="Create lesson", description="Creates lesson with conflict detection"),
)
class LessonViewSet(ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["teacher", "subject", "status"]
    ordering_fields = ["start_datetime"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Lesson.objects.none()

        user = self.request.user
        lessons = Lesson.objects.select_related("teacher", "student", "group", "subject")

        if user.role == User.Role.TEACHER:
            return lessons.filter(teacher=user)

        return lessons.filter(subject__branch__in=user.get_visible_branches())

@extend_schema(tags=["Attendance"]) 
@extend_schema_view(
    list=extend_schema(summary="List attendance"),
    create=extend_schema(summary="Mark attendance"),
)
class AttendanceViewSet(ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [CanManageAttendance]
    filterset_fields = ["lesson", "student", "status"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Attendance.objects.none()

        user = self.request.user
        attendance = Attendance.objects.select_related("lesson", "student")

        if user.role == User.Role.TEACHER:
            return attendance.filter(lesson__teacher=user)

        return attendance.filter(lesson__subject__branch__in=user.get_visible_branches())

    def perform_create(self, serializer):
        lesson = serializer.validated_data["lesson"]
        user = self.request.user

        if user.role == User.Role.TEACHER and lesson.teacher != user:
            raise PermissionDenied("You cannot mark attendance for another teacher's lesson.")

        attendance = serializer.save()

        if lesson.status == Lesson.Status.SCHEDULED:
            lesson.status = Lesson.Status.COMPLETED
            lesson.save()

    def perform_update(self, serializer):
        attendance = serializer.save()
        lesson = attendance.lesson
        user = self.request.user

        if user.role == User.Role.TEACHER and lesson.teacher != user:
            raise PermissionDenied("You cannot edit attendance for another teacher's lesson.")

        if lesson.status == Lesson.Status.SCHEDULED:
            lesson.status = Lesson.Status.COMPLETED
            lesson.save()

@extend_schema(tags=["Lesson Templates"]) 
@extend_schema_view(
    list=extend_schema(summary="List lesson templates"),
    create=extend_schema(summary="Create recurring lesson template"),
)
class LessonTemplateViewSet(ModelViewSet):
    serializer_class = LessonTemplateSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["teacher", "subject", "status"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return LessonTemplate.objects.none()

        user = self.request.user
        queryset = LessonTemplate.objects.select_related("teacher", "student", "group", "subject").prefetch_related("slots")

        if user.role == User.Role.TEACHER:
            return queryset.filter(teacher=user)

        return queryset.filter(subject__branch__in=user.get_visible_branches())