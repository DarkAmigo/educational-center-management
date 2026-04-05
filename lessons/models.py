from django.db import models
from users.models import User
from students.models import Student
from branches.models import Group, Subject

class Lesson(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='lessons')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='lessons')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lessons')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SCHEDULED)

    class Meta:
        ordering = ['start_datetime']

    def __str__(self):
        if self.student:
            return f"Individual Lesson: {self.subject.name} with {self.student}"
        if self.group:
            return f"Group Lesson: {self.subject.name} for {self.group}"
        return f"Lesson: {self.subject.name}"


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=10, choices=Status.choices)
    note = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('lesson', 'student')  

    def __str__(self):
        return f"{self.student} - {self.status} for {self.lesson}"
