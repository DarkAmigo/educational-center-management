from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from .models import SubscriptionPlan, StudentSubscription

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'subjects_list', 'type', 'status')
    list_filter = ('type', 'status', 'branch')
    search_fields = ('name',)
    filter_horizontal = ('subjects',)

    def subjects_list(self, obj):
        return ", ".join(obj.subjects.values_list('name', flat=True))

    subjects_list.short_description = 'Subjects'

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        try:
            form.instance.full_clean()
        except ValidationError as exc:
            self.message_user(request, "; ".join(exc.messages), level=messages.ERROR)

@admin.register(StudentSubscription)
class StudentSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('student', 'plan', 'subject', 'start_date')
    list_filter = ('subject', 'plan')
    search_fields = ('student__first_name', 'student__last_name')
