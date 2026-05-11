from config.serializers import CleanModelSerializer

from lessons.models import (
    Lesson,
    Attendance,
)


class LessonSerializer(CleanModelSerializer):

    class Meta:
        model = Lesson
        fields = "__all__"


class AttendanceSerializer(CleanModelSerializer):

    class Meta:
        model = Attendance
        fields = "__all__"