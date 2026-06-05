from datetime import date, datetime, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from branches.models import Branch, Subject
from lessons.models import Lesson
from students.models import Student
from users.models import User


class LessonConflictTests(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(
            name="Main branch",
            address="Main street, 1",
            city="Kyiv",
        )
        self.subject = Subject.objects.create(
            name="Python",
            branch=self.branch,
        )
        self.teacher = self.create_teacher("+380991112233")
        self.other_teacher = self.create_teacher("+380991112244")
        self.student = self.create_student("Ivan", "Petrenko")
        self.other_student = self.create_student("Olena", "Shevchenko")
        self.starts_at = timezone.make_aware(datetime(2026, 6, 8, 10, 0))
        self.ends_at = self.starts_at + timedelta(hours=1)

    def create_teacher(self, phone):
        return User.objects.create_user(
            phone=phone,
            password="StrongPass123",
            first_name="Teacher",
            last_name=phone[-4:],
            role=User.Role.TEACHER,
        )

    def create_student(self, first_name, last_name):
        return Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date(2010, 1, 1),
            phone="+380501112233",
            email=f"{first_name.lower()}@example.com",
            address="Student street, 1",
            parent_name="Parent",
            parent_phone="+380671112233",
            parent_email=f"parent.{first_name.lower()}@example.com",
            parent_relation="mother",
            branch=self.branch,
        )

    def create_lesson(self, **extra_fields):
        fields = {
            "teacher": self.teacher,
            "student": self.student,
            "subject": self.subject,
            "start_datetime": self.starts_at,
            "end_datetime": self.ends_at,
        }
        fields.update(extra_fields)
        return Lesson.objects.create(**fields)

    def build_lesson(self, **extra_fields):
        fields = {
            "teacher": self.teacher,
            "student": self.student,
            "subject": self.subject,
            "start_datetime": self.starts_at + timedelta(minutes=30),
            "end_datetime": self.ends_at + timedelta(minutes=30),
        }
        fields.update(extra_fields)
        return Lesson(**fields)

    def test_teacher_conflict(self):
        self.create_lesson(student=self.student)
        lesson = self.build_lesson(student=self.other_student)

        with self.assertRaisesMessage(
            ValidationError,
            "Teacher already has another lesson at this time.",
        ):
            lesson.full_clean()

    def test_student_conflict(self):
        self.create_lesson(teacher=self.teacher)
        lesson = self.build_lesson(teacher=self.other_teacher)

        with self.assertRaisesMessage(
            ValidationError,
            f"{self.student} already has another lesson at this time.",
        ):
            lesson.full_clean()

    def test_adjacent_lessons_allowed(self):
        self.create_lesson()
        lesson = self.build_lesson(
            start_datetime=self.ends_at,
            end_datetime=self.ends_at + timedelta(hours=1),
        )

        lesson.full_clean()

    def test_cancelled_lessons_ignored(self):
        self.create_lesson(status=Lesson.Status.CANCELLED)
        lesson = self.build_lesson()

        lesson.full_clean()
