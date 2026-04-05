from django.contrib import admin
from .models import Lesson, Attendance

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'student', 'group', 'start_datetime', 'end_datetime', 'status')
    list_filter = ('status', 'subject', 'teacher', 'group')
    search_fields = ('subject__name', 'teacher__first_name', 'teacher__last_name')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'student', 'status', 'note')
    list_filter = ('status',)
    search_fields = ('student__first_name', 'student__last_name', 'lesson__subject__name')
