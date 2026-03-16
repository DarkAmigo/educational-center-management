from django.db import models
from branches.models import Branch, Group

class Student(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    parent_name = models.CharField(max_length=255)
    parent_phone = models.CharField(max_length=20)
    parent_email = models.EmailField()
    parent_relation = models.CharField(max_length=50)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='students')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class GroupMembership(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='memberships')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    join_date = models.DateField()
    leave_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'group')

    def __str__(self):
        return f"{self.student} in {self.group}"