from rest_framework import serializers
from config.serializers import CleanModelSerializer
from lessons.models import Lesson, Attendance, LessonTemplate, LessonTemplateSlot

class LessonTemplateSlotSerializer(CleanModelSerializer):

    class Meta:
        model = LessonTemplateSlot
        fields = "__all__"
        read_only_fields = ("template",)

class LessonTemplateSerializer(CleanModelSerializer):

    slots = LessonTemplateSlotSerializer(
        many=True
    )

    class Meta:
        model = LessonTemplate
        fields = "__all__"

    def create(self, validated_data):

        slots_data = validated_data.pop("slots")

        template = LessonTemplate.objects.create(
            **validated_data
        )

        for slot_data in slots_data:

            LessonTemplateSlot.objects.create(
                template=template,
                **slot_data
            )

        template.generate_lessons()

        return template
    
class LessonSerializer(CleanModelSerializer):

    class Meta:
        model = Lesson
        fields = "__all__"

class AttendanceSerializer(CleanModelSerializer):

    class Meta:
        model = Attendance
        fields = "__all__"