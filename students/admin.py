from django.contrib import admin
from .models import Student, GroupMembership

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'email', 'branch', 'status')
    list_filter = ('status', 'branch')
    search_fields = ('first_name', 'last_name', 'phone', 'email')

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'join_date', 'leave_date')
    list_filter = ('group',)
    search_fields = ('student__first_name', 'student__last_name')
