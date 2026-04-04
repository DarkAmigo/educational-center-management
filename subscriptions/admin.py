from django.contrib import admin
from .models import SubscriptionPlan, StudentSubscription

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'type')
    list_filter = ('type', 'subject')
    search_fields = ('name',)

@admin.register(StudentSubscription)
class StudentSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('student', 'plan', 'subject', 'start_date')
    list_filter = ('subject',)
    search_fields = ('student__first_name', 'student__last_name')
