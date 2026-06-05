from datetime import date, datetime, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from branches.models import Branch, Subject
from lessons.models import Attendance, Lesson
from students.models import Student
from users.models import User


class LessonTestDataMixin:
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

    def create_admin(self, phone="+380991112255"):
        return User.objects.create_user(
            phone=phone,
            password="StrongPass123",
            first_name="Admin",
            last_name=phone[-4:],
            role=User.Role.ADMIN,
        )

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


class LessonPermissionTests(LessonTestDataMixin, APITestCase):
    def post_lesson(self, user):
        self.client.force_authenticate(user=user)
        return self.client.post(
            reverse("api-lessons-list"),
            {
                "teacher": self.teacher.pk,
                "student": self.student.pk,
                "subject": self.subject.pk,
                "start_datetime": self.starts_at.isoformat(),
                "end_datetime": self.ends_at.isoformat(),
            },
        )

    def test_admin_can_create_lesson(self):
        response = self.post_lesson(self.create_admin())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Lesson.objects.filter(
                teacher=self.teacher,
                student=self.student,
                subject=self.subject,
                start_datetime=self.starts_at,
                end_datetime=self.ends_at,
            ).exists()
        )

    def test_teacher_cannot_create_lesson(self):
        response = self.post_lesson(self.teacher)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 0)


class LessonConflictTests(LessonTestDataMixin, TestCase):
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


class AttendanceAPITests(LessonTestDataMixin, APITestCase):
    def post_attendance(self, lesson, student, attendance_status, user=None):
        self.client.force_authenticate(user=user or self.teacher)
        return self.client.post(
            reverse("api-attendance-list"),
            {
                "lesson": lesson.pk,
                "student": student.pk,
                "status": attendance_status,
            },
        )

    def test_mark_attendance(self):
        lesson = self.create_lesson()

        response = self.post_attendance(
            lesson,
            self.student,
            Attendance.Status.PRESENT,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        attendance = Attendance.objects.get(lesson=lesson, student=self.student)
        self.assertEqual(attendance.status, Attendance.Status.PRESENT)
        lesson.refresh_from_db()
        self.assertEqual(lesson.status, Lesson.Status.COMPLETED)

    def test_teacher_can_mark_own_lesson(self):
        lesson = self.create_lesson(teacher=self.teacher)

        response = self.post_attendance(
            lesson,
            self.student,
            Attendance.Status.PRESENT,
            user=self.teacher,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Attendance.objects.filter(
                lesson=lesson,
                student=self.student,
                status=Attendance.Status.PRESENT,
            ).exists()
        )

    def test_teacher_cannot_mark_other_lesson(self):
        lesson = self.create_lesson(teacher=self.other_teacher)

        response = self.post_attendance(
            lesson,
            self.student,
            Attendance.Status.PRESENT,
            user=self.teacher,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            Attendance.objects.filter(
                lesson=lesson,
                student=self.student,
            ).exists()
        )

    def test_duplicate_attendance_updates_record(self):
        lesson = self.create_lesson()
        self.post_attendance(
            lesson,
            self.student,
            Attendance.Status.PRESENT,
        )

        response = self.post_attendance(
            lesson,
            self.student,
            Attendance.Status.ABSENT,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Attendance.objects.filter(
                lesson=lesson,
                student=self.student,
            ).count(),
            1,
        )
        attendance = Attendance.objects.get(lesson=lesson, student=self.student)
        self.assertEqual(attendance.status, Attendance.Status.ABSENT)
