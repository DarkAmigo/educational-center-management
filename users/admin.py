from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'first_name', 'last_name', 'role', 'branches_list', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'assigned_branches')
    search_fields = ('phone', 'first_name', 'last_name')
    filter_horizontal = ('assigned_branches', 'groups', 'user_permissions')

    def branches_list(self, obj):
        return ", ".join(obj.assigned_branches.values_list('name', flat=True))

    branches_list.short_description = 'Branches'
