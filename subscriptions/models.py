from django.db import models
from django.core.exceptions import ValidationError
from branches.models import Branch, Subject
from students.models import Student

class SubscriptionPlan(models.Model):
    class PlanType(models.TextChoices):
        GROUP = 'group', 'Group'
        INDIVIDUAL = 'individual', 'Individual'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'

    name = models.CharField(max_length=255)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='subscription_plans')
    subjects = models.ManyToManyField(Subject, related_name='subscription_plans', blank=True)
    type = models.CharField(max_length=10, choices=PlanType.choices)
    pricing_grid = models.JSONField(default=dict)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    def clean(self):
        errors = {}

        if not isinstance(self.pricing_grid, dict) or not self.pricing_grid:
            errors['pricing_grid'] = 'Pricing grid cannot be empty.'

        if self.pk and self.branch_id:
            wrong_subjects = self.subjects.exclude(branch_id=self.branch_id)
            if wrong_subjects.exists():
                errors['subjects'] = 'All subjects in the plan must belong to the selected branch.'

            if not self.subjects.exists():
                errors['subjects'] = 'Choose at least one subject for the plan.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.name} ({self.branch.name})"


class StudentSubscription(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='student_subscriptions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_date = models.DateField()

    def clean(self):
        errors = {}

        if self.student_id and self.student.status != Student.Status.ACTIVE:
            errors['student'] = 'Archived student cannot receive a new subscription.'

        if self.plan_id:
            if self.plan.status != SubscriptionPlan.Status.ACTIVE:
                errors['plan'] = 'Archived plan cannot be assigned.'

            if self.student_id and self.student.branch_id != self.plan.branch_id:
                errors['plan'] = 'Student and plan must belong to the same branch.'

        if self.subject_id and self.plan_id:
            if self.subject.branch_id != self.plan.branch_id:
                errors['subject'] = 'Subject must belong to the same branch as the plan.'

            if self.subject.status != Subject.Status.ACTIVE:
                errors['subject'] = 'Archived subject cannot be assigned.'

            if not self.plan.subjects.filter(pk=self.subject_id).exists():
                errors['subject'] = 'This subject is not included in the selected plan.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.student} - {self.plan}"
