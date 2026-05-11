from config.serializers import CleanModelSerializer

from lessons.models import (
    Lesson,
    Attendance,
)
from rest_framework import serializers
from django.core.exceptions import ValidationError


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = "__all__"

    def validate(self, attrs):
        instance = self.instance

        data = {}

        if instance:
            for field in Lesson._meta.fields:
                data[field.name] = getattr(instance, field.name)

        data.update(attrs)

        obj = Lesson(**data)

        if instance:
            obj.pk = instance.pk

        try:
            obj.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs

class AttendanceSerializer(CleanModelSerializer):

    class Meta:
        model = Attendance
        fields = "__all__"