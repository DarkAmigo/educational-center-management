from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import Attendance, Lesson, LessonTemplate, LessonTemplateSlot


class LessonTemplateSlotInline(admin.TabularInline):
    model = LessonTemplateSlot
    extra = 1


@admin.register(LessonTemplate)
class LessonTemplateAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'student', 'group', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'subject', 'teacher')
    search_fields = ('subject__name', 'teacher__first_name', 'teacher__last_name')
    inlines = [LessonTemplateSlotInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        template = form.instance
        if template.status == LessonTemplate.Status.ACTIVE and not template.lessons.exists():
            try:
                template.generate_lessons()
                self.message_user(request, 'Lessons were generated from the template.')
            except ValidationError as exc:
                self.message_user(request, "; ".join(exc.messages), level=messages.ERROR)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'student', 'group', 'template', 'start_datetime', 'end_datetime', 'status')
    list_filter = ('status', 'subject', 'teacher', 'group')
    search_fields = ('subject__name', 'teacher__first_name', 'teacher__last_name')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'student', 'status', 'note')
    list_filter = ('status',)
    search_fields = ('student__first_name', 'student__last_name', 'lesson__subject__name')
