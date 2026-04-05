from django.db import models
from branches.models import Subject
from students.models import Student

class SubscriptionPlan(models.Model):
    class PlanType(models.TextChoices):
        GROUP = 'group', 'Group'
        INDIVIDUAL = 'individual', 'Individual'

    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='plans')
    type = models.CharField(max_length=10, choices=PlanType.choices)
    pricing_grid = models.JSONField() 

    def __str__(self):
        return f"{self.name} ({self.subject.name})"


class StudentSubscription(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='student_subscriptions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_date = models.DateField()

    def __str__(self):
        return f"{self.student} - {self.plan}"
