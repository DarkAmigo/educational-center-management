from django.contrib import admin
from .models import Branch, Subject, Group

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'address', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'city', 'address')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'status')
    list_filter = ('status', 'branch')
    search_fields = ('name',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'status')
    list_filter = ('status', 'branch')
    search_fields = ('name',)
