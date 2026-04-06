from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F, Q
from django.utils import timezone

from branches.models import Group, Subject
from students.models import GroupMembership, Student
from users.models import User


def get_group_students_for_date(group, lesson_date):
    return Student.objects.filter(
        status=Student.Status.ACTIVE,
        memberships__group=group,
        memberships__join_date__lte=lesson_date,
    ).filter(
        Q(memberships__leave_date__isnull=True) | Q(memberships__leave_date__gte=lesson_date)
    ).distinct()


class LessonTemplate(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_templates')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='lesson_templates')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='lesson_templates')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lesson_templates')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ['start_date']
        constraints = [
            models.CheckConstraint(
                condition=Q(start_date__lte=F('end_date')),
                name='lessontemplate_start_date_before_end_date',
            ),
            models.CheckConstraint(
                condition=(
                    (Q(student__isnull=False) & Q(group__isnull=True)) |
                    (Q(student__isnull=True) & Q(group__isnull=False))
                ),
                name='lessontemplate_student_or_group_only',
            ),
        ]

    def clean(self):
        errors = {}

        if self.teacher_id and self.teacher.role != User.Role.TEACHER:
            errors['teacher'] = 'Choose a teacher user.'

        if self.student_id and self.group_id:
            errors['group'] = 'Choose either student or group.'

        if not self.student_id and not self.group_id:
            errors['student'] = 'Choose a student or a group.'

        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors['end_date'] = 'End date cannot be earlier than start date.'

        if self.subject_id and self.subject.status != Subject.Status.ACTIVE and self.status == self.Status.ACTIVE:
            errors['subject'] = 'Archived subject cannot be used in an active template.'

        if self.student_id:
            if self.student.status != Student.Status.ACTIVE:
                errors['student'] = 'Archived student cannot be used in a template.'

            if self.subject_id and self.student.branch_id != self.subject.branch_id:
                errors['student'] = 'Student and subject must belong to the same branch.'

        if self.group_id:
            if self.group.status != Group.Status.ACTIVE and self.status == self.Status.ACTIVE:
                errors['group'] = 'Archived group cannot be used in an active template.'

            if self.subject_id and self.group.branch_id != self.subject.branch_id:
                errors['group'] = 'Group and subject must belong to the same branch.'

        if errors:
            raise ValidationError(errors)

    def generate_lessons(self):
        slots = list(self.slots.all())

        if not slots:
            raise ValidationError('Add at least one weekly slot to the template.')

        if self.lessons.exists():
            return

        current_date = self.start_date
        current_timezone = timezone.get_current_timezone()

        with transaction.atomic():
            while current_date <= self.end_date:
                for slot in slots:
                    if slot.weekday != current_date.weekday():
                        continue

                    start_datetime = timezone.make_aware(
                        datetime.combine(current_date, slot.start_time),
                        current_timezone,
                    )
                    end_datetime = timezone.make_aware(
                        datetime.combine(current_date, slot.end_time),
                        current_timezone,
                    )

                    lesson = Lesson(
                        teacher=self.teacher,
                        student=self.student,
                        group=self.group,
                        subject=self.subject,
                        template=self,
                        start_datetime=start_datetime,
                        end_datetime=end_datetime,
                    )
                    lesson.full_clean()
                    lesson.save()

                current_date += timedelta(days=1)

    def __str__(self):
        return f"Template: {self.subject.name}"


class LessonTemplateSlot(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, 'Monday'
        TUESDAY = 1, 'Tuesday'
        WEDNESDAY = 2, 'Wednesday'
        THURSDAY = 3, 'Thursday'
        FRIDAY = 4, 'Friday'
        SATURDAY = 5, 'Saturday'
        SUNDAY = 6, 'Sunday'

    template = models.ForeignKey(LessonTemplate, on_delete=models.CASCADE, related_name='slots')
    weekday = models.IntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['weekday', 'start_time']
        unique_together = ('template', 'weekday', 'start_time', 'end_time')
        constraints = [
            models.CheckConstraint(
                condition=Q(start_time__lt=F('end_time')),
                name='lessontemplateslot_start_time_before_end_time',
            ),
        ]

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({'end_time': 'End time must be later than start time.'})

    def __str__(self):
        return f"{self.get_weekday_display()} {self.start_time}-{self.end_time}"


class Lesson(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='lessons')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='lessons')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lessons')
    template = models.ForeignKey(LessonTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SCHEDULED)

    class Meta:
        ordering = ['start_datetime']
        constraints = [
            models.CheckConstraint(
                condition=Q(start_datetime__lt=F('end_datetime')),
                name='lesson_start_datetime_before_end_datetime',
            ),
            models.CheckConstraint(
                condition=(
                    (Q(student__isnull=False) & Q(group__isnull=True)) |
                    (Q(student__isnull=True) & Q(group__isnull=False))
                ),
                name='lesson_student_or_group_only',
            ),
        ]

    def get_participant_students(self):
        if self.student_id:
            return Student.objects.filter(pk=self.student_id)

        if self.group_id and self.start_datetime:
            return get_group_students_for_date(self.group, self.start_datetime.date())

        return Student.objects.none()

    def clean(self):
        errors = {}
        conflict_messages = []

        if self.teacher_id and self.teacher.role != User.Role.TEACHER:
            errors['teacher'] = 'Choose a teacher user.'

        if self.student_id and self.group_id:
            errors['group'] = 'Choose either student or group.'

        if not self.student_id and not self.group_id:
            errors['student'] = 'Choose a student or a group.'

        if self.start_datetime and self.end_datetime and self.start_datetime >= self.end_datetime:
            errors['end_datetime'] = 'End time must be later than start time.'

        if self.subject_id and self.subject.status != Subject.Status.ACTIVE and self.status != self.Status.CANCELLED:
            errors['subject'] = 'Archived subject cannot be used for a new lesson.'

        if self.student_id:
            if self.student.status != Student.Status.ACTIVE:
                errors['student'] = 'Archived student cannot be used for a new lesson.'

            if self.subject_id and self.student.branch_id != self.subject.branch_id:
                errors['student'] = 'Student and subject must belong to the same branch.'

        if self.group_id:
            if self.group.status != Group.Status.ACTIVE and self.status != self.Status.CANCELLED:
                errors['group'] = 'Archived group cannot be used for a new lesson.'

            if self.subject_id and self.group.branch_id != self.subject.branch_id:
                errors['group'] = 'Group and subject must belong to the same branch.'

        if errors:
            raise ValidationError(errors)

        if (
            self.status != self.Status.CANCELLED
            and self.teacher_id
            and self.start_datetime
            and self.end_datetime
        ):
            overlapping_lessons = Lesson.objects.filter(
                start_datetime__lt=self.end_datetime,
                end_datetime__gt=self.start_datetime,
            ).exclude(status=self.Status.CANCELLED)

            if self.pk:
                overlapping_lessons = overlapping_lessons.exclude(pk=self.pk)

            teacher_conflicts = overlapping_lessons.filter(teacher=self.teacher)
            if teacher_conflicts.exists():
                conflict_messages.append('Teacher already has another lesson at this time.')

            lesson_date = self.start_datetime.date()
            for student in self.get_participant_students():
                student_conflicts = overlapping_lessons.filter(
                    Q(student=student) |
                    Q(
                        group__memberships__student=student,
                        group__memberships__join_date__lte=lesson_date,
                    )
                ).filter(
                    Q(group__memberships__leave_date__isnull=True) |
                    Q(group__memberships__leave_date__gte=lesson_date) |
                    Q(student=student)
                ).distinct()

                if student_conflicts.exists():
                    conflict_messages.append(f'{student} already has another lesson at this time.')

        if conflict_messages:
            raise ValidationError(conflict_messages)

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

    def clean(self):
        errors = {}

        if self.lesson_id and self.lesson.status == Lesson.Status.CANCELLED:
            errors['lesson'] = 'Cannot mark attendance for a cancelled lesson.'

        if self.lesson_id and self.student_id:
            if self.lesson.student_id:
                if self.lesson.student_id != self.student_id:
                    errors['student'] = 'This student does not belong to the lesson.'
            elif self.lesson.group_id:
                lesson_date = self.lesson.start_datetime.date()
                is_member = GroupMembership.objects.filter(
                    student=self.student,
                    group=self.lesson.group,
                    join_date__lte=lesson_date,
                ).filter(
                    Q(leave_date__isnull=True) | Q(leave_date__gte=lesson_date)
                ).exists()

                if not is_member:
                    errors['student'] = 'This student does not belong to the lesson group.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.student} - {self.status} for {self.lesson}"
