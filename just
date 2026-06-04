Дивись у мене є вже готові 2 фази наче ось:
у мене проект ділиться на такі app, як: branches, core, lessons, students, subscriptions, users. Ще є такі директорії, як config та templates.
Ось, що відбувається у app branches:
є папка api де є:
serializers.py:
from config.serializers import CleanModelSerializer
from branches.models import Branch, Subject, Group

class BranchSerializer(CleanModelSerializer):
    
    class Meta:
        model = Branch
        fields = "__all__"


class SubjectSerializer(CleanModelSerializer):

    class Meta:
        model = Subject
        fields = "__all__"


class GroupSerializer(CleanModelSerializer):

    class Meta:
        model = Group
        fields = "__all__"

urls.py:
from rest_framework.routers import DefaultRouter
from .views import BranchViewSet, SubjectViewSet, GroupViewSet

router = DefaultRouter()

router.register("branches", BranchViewSet, basename="api-branches")
router.register("subjects", SubjectViewSet, basename="api-subjects")
router.register("groups", GroupViewSet, basename="api-groups")

urlpatterns = router.urls

views.py:
from rest_framework.viewsets import ModelViewSet
from config.permissions import IsAdminOrReadOnly
from branches.models import Branch, Subject, Group
from .serializers import BranchSerializer, SubjectSerializer, GroupSerializer

class BranchViewSet(ModelViewSet):

    serializer_class = BranchSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = ["status", "city"]
    search_fields = ["name"]

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Branch.objects.none()

        return self.request.user.get_visible_branches()


class SubjectViewSet(ModelViewSet):

    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = ["status", "branch"]
    search_fields = ["name"]

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Subject.objects.none()

        return Subject.objects.filter(
            branch__in=self.request.user.get_visible_branches()
        )


class GroupViewSet(ModelViewSet):

    serializer_class = GroupSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = ["status", "branch"]
    search_fields = ["name"]

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Group.objects.none()

        return Group.objects.filter(
            branch__in=self.request.user.get_visible_branches()
        )

є директорія templates/branches:
branches.html:
{% extends "base.html" %}

{% block content %}
<h2>Branches</h2>

<table border="1">
<tr>
    <th>Name</th>
    <th>City</th>
    <th>Address</th>
    <th>Status</th>
</tr>

{% for b in branches %}
<tr>
    <td>{{ b.name }}</td>
    <td>{{ b.city }}</td>
    <td>{{ b.address }}</td>
    <td>{{ b.status }}</td>
</tr>
{% endfor %}
</table>

{% endblock %}

у просто директорії branches є таке:
models.py:
from django.db import models

class Branch(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    def __str__(self):
        return self.name


class Subject(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'

    name = models.CharField(max_length=255)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='subjects')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        unique_together = ('branch', 'name')

    def __str__(self):
        return f"{self.name} ({self.branch.name})"


class Group(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'

    name = models.CharField(max_length=255)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='groups')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    def __str__(self):
        return f"{self.name} ({self.branch.name})"

urls.py:
from django.urls import path
from .views import branches_view

urlpatterns = [
    path("branches/", branches_view, name="branches"),
]

views.py:
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import User


@login_required
def branches_view(request):
    if request.user.role != User.Role.ADMIN:
        return redirect("dashboard")

    branches = request.user.get_visible_branches()

    return render(request, "branches/branches.html", {
        "branches": branches
    })

у директорії config:
permissions.py:
from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models import User


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return request.user.role == User.Role.ADMIN
    
class CanManageAttendance(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        return request.user.role in [
            User.Role.ADMIN,
            User.Role.TEACHER,
        ]

    def has_object_permission(self, request, view, obj):

        if request.user.role == User.Role.ADMIN:
            return True

        return obj.lesson.teacher == request.user

serializers.py:
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

class CleanModelSerializer(serializers.ModelSerializer):

    def validate(self, attrs):

        model_class = self.Meta.model

        data = {}

        if self.instance:
            for field in model_class._meta.fields:
                data[field.name] = getattr(self.instance, field.name)

        data.update(attrs)

        obj = model_class(**data)

        if self.instance:
            obj.pk = self.instance.pk

        try:
            obj.full_clean()

        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs

settings.py:
from pathlib import Path
import os
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6ve&%7rj_z_d4&xim8v1+s7(79d9-(s=&x-4w(c%--t&tos+6d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'branches',
    'core',
    'lessons',
    'students',
    'subscriptions',
    'users',
    'django_filters',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  
        'APP_DIRS': True,                   
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',  
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "education_center",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,

    "AUTH_HEADER_TYPES": ("Bearer",),
}

AUTHENTICATION_BACKENDS = [
    "users.backends.PhoneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

SPECTACULAR_SETTINGS = {
    "TITLE": "EduProject API",
    "DESCRIPTION": "REST API documentation for education management system",
    "VERSION": "1.0.0",

    "SERVE_INCLUDE_SCHEMA": False,

    "COMPONENT_SPLIT_REQUEST": True,

    "SECURITY": [{"BearerAuth": []}],

    "COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },

    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],

    "ENUM_NAME_OVERRIDES": {
        "LessonStatusEnum": "lessons.models.Lesson.Status",
        "AttendanceStatusEnum": "lessons.models.Attendance.Status",
        "TemplateStatusEnum": "lessons.models.LessonTemplate.Status",
    }
}

SPECTACULAR_SETTINGS["AUTHENTICATION_WHITELIST"] = [
    "rest_framework_simplejwt.authentication.JWTAuthentication",
]

SPECTACULAR_SETTINGS.update({
    "ENUM_NAME_OVERRIDES": {
        "LessonStatusEnum": "lessons.models.Lesson.Status",
        "AttendanceStatusEnum": "lessons.models.Attendance.Status",
        "TemplateStatusEnum": "lessons.models.LessonTemplate.Status",
    }
})

urls.py:
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path("", include("users.urls")),
    path("", include("core.urls")),
    path("", include("branches.urls")),
    path("", include("students.urls")),
    path("", include("lessons.urls")),

    path("api/auth/", include("users.api.urls")),
    path("api/", include("branches.api.urls")),
    path("api/students/", include("students.api.urls")),
    path("api/", include("lessons.api.urls")),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("docs/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

директорія core:
templates/core/dashboard.html:
{% extends "base.html" %}

{% block content %}
<h2>Dashboard</h2>

{% if user.role == "ADMIN" %}
    <p>Branches: {{ branches_count }}</p>
    <p>Students: {{ students_count }}</p>
    <p>Teachers: {{ teachers_count }}</p>
{% endif %}

<h3>Today's Lessons</h3>

<ul>
{% for lesson in lessons %}
    <li>{{ lesson.start_datetime }} - {{ lesson.subject.name }}</li>
{% endfor %}
</ul>

{% endblock %}

urls.py:
from django.urls import path
from .views import dashboard_view, home_view

urlpatterns = [
    path("", home_view),
    path("dashboard/", dashboard_view, name="dashboard"),
]

views.py:
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from students.models import Student
from lessons.models import Lesson
from users.models import User


def home_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    return redirect("/login/")


@login_required
def dashboard_view(request):

    user = request.user

    context = {}

    if user.role == User.Role.ADMIN:

        branches = user.get_visible_branches()

        context["branches_count"] = branches.count()

        context["students_count"] = Student.objects.filter(
            branch__in=branches
        ).count()

        context["teachers_count"] = User.objects.filter(
            role=User.Role.TEACHER,
            lessons__subject__branch__in=branches,
        ).distinct().count()

    today = now().date()

    lessons = Lesson.objects.filter(
        start_datetime__date=today
    )

    if user.role == User.Role.TEACHER:

        lessons = lessons.filter(
            teacher=user
        )

    elif not user.is_superuser:

        lessons = lessons.filter(
            subject__branch__in=user.get_visible_branches()
        )

    context["lessons"] = lessons

    return render(
        request,
        "core/dashboard.html",
        context,
    )

директорія lessons:
api: 
serializers.py:
from rest_framework import serializers
from config.serializers import CleanModelSerializer
from lessons.models import Lesson, Attendance, LessonTemplate, LessonTemplateSlot

class LessonTemplateSlotSerializer(CleanModelSerializer):

    class Meta:
        model = LessonTemplateSlot
        fields = "__all__"


class LessonTemplateSerializer(CleanModelSerializer):

    slots = LessonTemplateSlotSerializer(
        many=True
    )

    class Meta:
        model = LessonTemplate
        fields = "__all__"

    def create(self, validated_data):

        slots_data = validated_data.pop("slots")

        template = LessonTemplate.objects.create(
            **validated_data
        )

        for slot_data in slots_data:

            LessonTemplateSlot.objects.create(
                template=template,
                **slot_data
            )

        template.generate_lessons()

        return template
    
class LessonSerializer(CleanModelSerializer):

    class Meta:
        model = Lesson
        fields = "__all__"

class AttendanceSerializer(CleanModelSerializer):

    class Meta:
        model = Attendance
        fields = "__all__"

urls.py:
from rest_framework.routers import DefaultRouter
from .views import LessonViewSet, AttendanceViewSet, LessonTemplateViewSet

router = DefaultRouter()

router.register("lessons", LessonViewSet, basename="api-lessons")
router.register("attendance", AttendanceViewSet, basename="api-attendance")
router.register("lesson-templates", LessonTemplateViewSet, basename="api-lesson-templates")

urlpatterns = router.urls

views.py:
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema, extend_schema_view
from users.models import User
from lessons.models import (Lesson, Attendance, LessonTemplate)
from config.permissions import (IsAdminOrReadOnly, CanManageAttendance)
from .serializers import (LessonSerializer, AttendanceSerializer, LessonTemplateSerializer)

@extend_schema_view(
    list=extend_schema(
        summary="List lessons"
    ),
    create=extend_schema(
        summary="Create lesson",
        description="Creates lesson with conflict detection",
    ),
)

class LessonViewSet(ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = [
        "teacher",
        "subject",
        "status",
    ]

    ordering_fields = [
        "start_datetime",
    ]

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Lesson.objects.none()

        user = self.request.user

        lessons = Lesson.objects.select_related(
            "teacher",
            "student",
            "group",
            "subject",
        )

        if user.role == User.Role.TEACHER:
            return lessons.filter(
                teacher=user
            )

        return lessons.filter(
            subject__branch__in=user.get_visible_branches()
        )


@extend_schema_view(
    list=extend_schema(
        summary="List attendance"
    ),
    create=extend_schema(
        summary="Mark attendance"
    ),
)

class AttendanceViewSet(ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [CanManageAttendance]

    filterset_fields = [
        "lesson",
        "student",
        "status",
    ]

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Attendance.objects.none()

        user = self.request.user

        attendance = Attendance.objects.select_related(
            "lesson",
            "student",
        )

        if user.role == User.Role.TEACHER:
            return attendance.filter(
                lesson__teacher=user
            )

        return attendance.filter(
            lesson__subject__branch__in=user.get_visible_branches()
        )

    def perform_create(self, serializer):

        lesson = serializer.validated_data["lesson"]

        user = self.request.user

        if (
            user.role == User.Role.TEACHER
            and lesson.teacher != user
        ):
            raise PermissionDenied(
                "You cannot mark attendance for another teacher's lesson."
            )

        attendance = serializer.save()

        if lesson.status == Lesson.Status.SCHEDULED:
            lesson.status = Lesson.Status.COMPLETED
            lesson.save()

    def perform_update(self, serializer):

        attendance = serializer.save()

        lesson = attendance.lesson

        user = self.request.user

        if (
            user.role == User.Role.TEACHER
            and lesson.teacher != user
        ):
            raise PermissionDenied(
                "You cannot edit attendance for another teacher's lesson."
            )

        if lesson.status == Lesson.Status.SCHEDULED:
            lesson.status = Lesson.Status.COMPLETED
            lesson.save()
        
@extend_schema_view(
    list=extend_schema(
        summary="List lesson templates"
    ),
    create=extend_schema(
        summary="Create recurring lesson template"
    ),
)
class LessonTemplateViewSet(ModelViewSet):
    serializer_class = LessonTemplateSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = [
        "teacher",
        "subject",
        "status",
    ]

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return LessonTemplate.objects.none()

        user = self.request.user

        queryset = LessonTemplate.objects.select_related(
            "teacher",
            "student",
            "group",
            "subject",
        ).prefetch_related(
            "slots"
        )

        if user.role == User.Role.TEACHER:
            return queryset.filter(
                teacher=user
            )

        return queryset.filter(
            subject__branch__in=user.get_visible_branches()
        )

templates/lessons/schedule.html:
{% extends "base.html" %}

{% block content %}
<h2>Schedule</h2>

<ul>
{% for l in lessons %}
    <li>
        {{ l.start_datetime }} - {{ l.subject.name }}
        {% if l.student %}
            - {{ l.student }}
        {% elif l.group %}
            - {{ l.group }}
        {% endif %}
        ({{ l.status }})
    </li>
{% endfor %}
</ul>

{% endblock %}

просто директорія lessons:
models.py:
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

urls.py:
from django.urls import path
from .views import schedule_view

urlpatterns = [
    path("schedule/", schedule_view, name="schedule"),
]

views.py:
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Lesson
from users.models import User


@login_required
def schedule_view(request):
    user = request.user

    lessons = Lesson.objects.select_related(
        "teacher", "student", "group", "subject", "template"
    )

    if user.role == User.Role.TEACHER:
        lessons = lessons.filter(teacher=user)
    elif not user.is_superuser:
        lessons = lessons.filter(subject__branch__in=user.get_visible_branches())

    return render(request, "lessons/schedule.html", {
        "lessons": lessons
    })

app students:
api:
serializers.py:
from config.serializers import CleanModelSerializer
from students.models import Student

class StudentSerializer(CleanModelSerializer):

    class Meta:
        model = Student
        fields = "__all__"

urls.py:
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet

router = DefaultRouter()

router.register("", StudentViewSet, basename="api-students")

urlpatterns = router.urls

views.py:
from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from users.models import User
from students.models import Student
from config.permissions import IsAdminOrReadOnly
from .serializers import StudentSerializer

class StudentViewSet(ModelViewSet):

    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = ["branch", "status"]

    search_fields = [
        "first_name",
        "last_name",
        "phone",
    ]

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Student.objects.none()

        user = self.request.user

        students = Student.objects.select_related("branch")

        if user.role == User.Role.ADMIN:

            if user.is_superuser:
                return students

            return students.filter(
                branch__in=user.get_visible_branches()
            )

        return students.filter(
            Q(lessons__teacher=user) |
            Q(memberships__group__lessons__teacher=user)
        ).distinct()

templates/students:
list.html:
{% extends "base.html" %}

{% block content %}

<h1 class="text-3xl font-bold text-green-500 mb-6">
    Students
</h1>

<div id="students-container" class="grid gap-4">
</div>

<script>

async function loadStudents() {

    const response = await fetch("/api/students/", {
        headers: {
            "Authorization": "Bearer " + localStorage.getItem("access")
        }
    })

    const data = await response.json()

    const container = document.getElementById("students-container")

    container.innerHTML = ""

    data.results.forEach(student => {

        container.innerHTML += `
            <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-4">

                <h2 class="text-xl font-semibold">
                    ${student.first_name} ${student.last_name}
                </h2>

                <p class="text-zinc-400">
                    ${student.phone || ""}
                </p>

            </div>
        `
    })
}

loadStudents()

</script>

{% endblock %}

students.html:
{% extends "base.html" %}

{% block content %}
<h2>Students</h2>

<table border="1">
<tr>
    <th>Name</th>
    <th>Branch</th>
    <th>Status</th>
    <th>Phone</th>
    <th>Email</th>
</tr>
{% for s in students %}
<tr>
    <td>{{ s.first_name }} {{ s.last_name }}</td>
    <td>{{ s.branch.name }}</td>
    <td>{{ s.status }}</td>
    <td>{{ s.phone }}</td>
    <td>{{ s.email }}</td>
</tr>
{% endfor %}
</table>

{% endblock %}

просто диреторія students:
models.py:
from django.db import models
from django.db.models import F, Q
from django.core.exceptions import ValidationError
from branches.models import Branch, Group

class Student(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'

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
        constraints = [
            models.CheckConstraint(
                condition=Q(leave_date__isnull=True) | Q(leave_date__gte=F('join_date')),
                name='groupmembership_leave_date_after_join_date',
            ),
        ]

    def clean(self):
        errors = {}

        if self.student_id and self.group_id and self.student.branch_id != self.group.branch_id:
            errors['group'] = 'Student and group must belong to the same branch.'

        if self.leave_date and self.join_date and self.leave_date < self.join_date:
            errors['leave_date'] = 'Leave date cannot be earlier than join date.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.student} in {self.group}"

urls.py:
from django.urls import path
from .views import students_view

urlpatterns = [
    path("students/", students_view, name="students"),
]

views.py:
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from users.models import User
from .models import Student


@login_required
def students_view(request):
    students = Student.objects.select_related("branch").all()

    if request.user.role == User.Role.ADMIN:
        if not request.user.is_superuser:
            students = students.filter(branch__in=request.user.get_visible_branches())
    else:
        students = students.filter(
            Q(lessons__teacher=request.user) |
            Q(memberships__group__lessons__teacher=request.user)
        ).distinct()

    return render(request, "students/students.html", {
        "students": students
    })

app subscriptions:
models.py:
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

директорія templates:
base.html:
<!DOCTYPE html>
<html>

<head>
    <title>EduProject</title>

    <script src="https://cdn.tailwindcss.com"></script>
</head>

<body class="bg-black text-white min-h-screen">

    {% if user.is_authenticated %}

    <div class="bg-zinc-900 border-b border-green-500 p-4 flex gap-4 items-center">

        <p class="text-green-400 font-semibold">
            {{ user.phone }} ({{ user.role }})
        </p>

        <a href="/dashboard/" class="hover:text-green-400">
            Dashboard
        </a>

        {% if user.role == "ADMIN" %}
        <a href="/branches/" class="hover:text-green-400">
            Branches
        </a>
        {% endif %}

        <a href="/students/" class="hover:text-green-400">
            Students
        </a>

        <a href="/schedule/" class="hover:text-green-400">
            Schedule
        </a>

        <a href="/logout/" class="hover:text-red-400">
            Logout
        </a>

    </div>

    {% else %}

    <div class="p-4">
        <a href="/login/" class="text-green-400 hover:text-green-300">
            Login
        </a>
    </div>

    {% endif %}

    <div class="p-6">

        {% if messages %}
        {% for message in messages %}
        <div class="bg-zinc-900 border border-green-500 rounded-lg p-3 mb-4">
            {{ message }}
        </div>
        {% endfor %}
        {% endif %}

        {% block content %}
        {% endblock %}

    </div>

</body>

</html>

app users:
api:
serializers.py:
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers

class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):

    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    username_field = "phone"

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserInfoSerializer(self.user).data
        return data

urls.py:
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import PhoneTokenObtainPairView

urlpatterns = [
    path("login/", PhoneTokenObtainPairView.as_view(), name="jwt-login"),
    path("refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
]

views.py:
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import PhoneTokenObtainPairSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(
    request=PhoneTokenObtainPairSerializer,
    responses=PhoneTokenObtainPairSerializer
)

class PhoneTokenObtainPairView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer

templates/users:
login.html:
{% extends "base.html" %}

{% block content %}
<h2>Login</h2>

<form method="post">
    {% csrf_token %}
    <input type="text" name="phone" placeholder="Phone">
    <input type="password" name="password" placeholder="Password">
    <button type="submit">Login</button>
</form>

{% endblock %}

просто директорія users:
api_views.py:
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .permissions import IsAdminRole, IsTeacherRole
from .serializers import (
    LogoutSerializer,
    PhoneTokenObtainPairSerializer,
    UserInfoSerializer,
)


class PhoneLoginAPIView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = PhoneTokenObtainPairSerializer


class PhoneRefreshAPIView(TokenRefreshView):
    permission_classes = [AllowAny]


class LogoutAPIView(GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
        except TokenError:
            return Response(
                {'detail': 'Invalid refresh token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class MeAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(UserInfoSerializer(request.user).data)


class AdminRoleCheckAPIView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        return Response({'detail': 'Admin access granted.'})


class TeacherRoleCheckAPIView(APIView):
    permission_classes = [IsTeacherRole]

    def get(self, request, *args, **kwargs):
        return Response({'detail': 'Teacher access granted.'})

backends.py:
from django.contrib.auth.backends import BaseBackend
from .models import User


class PhoneBackend(BaseBackend):

    def authenticate(self, request, phone=None, password=None):
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None

models.py:
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from branches.models import Branch

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Phone must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        TEACHER = 'TEACHER', 'Teacher'

    phone = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=Role.choices)
    assigned_branches = models.ManyToManyField(Branch, blank=True, related_name='assigned_users')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_visible_branches(self):
        if self.is_superuser:
            return Branch.objects.all()

        if self.is_authenticated:
            return self.assigned_branches.all()

        return Branch.objects.none()

    def can_access_branch(self, branch_id):
        if self.is_superuser:
            return True

        if not self.is_authenticated:
            return False

        return self.assigned_branches.filter(pk=branch_id).exists()

    def __str__(self):
        return f"{self.phone} ({self.role})"

permissions.py:
from rest_framework.permissions import BasePermission
from .models import User


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and (
                user.is_superuser or user.role == User.Role.ADMIN
            )
        )


class IsTeacherRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and (
                user.is_superuser or user.role == User.Role.TEACHER
            )
        )

serializers.py:
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class BranchInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    city = serializers.CharField()


class UserInfoSerializer(serializers.ModelSerializer):
    accessible_branches = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'phone',
            'first_name',
            'last_name',
            'role',
            'accessible_branches',
        )

    def get_accessible_branches(self, obj):
        branches = obj.get_visible_branches().values('id', 'name', 'city')
        return BranchInfoSerializer(branches, many=True).data


class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': 'Invalid phone or password.',
    }

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserInfoSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

urls.py:
from django.urls import path
from .api_views import (
    AdminRoleCheckAPIView,
    LogoutAPIView,
    MeAPIView,
    PhoneLoginAPIView,
    PhoneRefreshAPIView,
    TeacherRoleCheckAPIView,
    TokenObtainPairView, 
    TokenRefreshView,
)
from .views import login_view, logout_view

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/login/", PhoneLoginAPIView.as_view(), name="api-login"),
    path("api/auth/refresh/", PhoneRefreshAPIView.as_view(), name="api-refresh"),
    path("api/auth/logout/", LogoutAPIView.as_view(), name="api-logout"),
    path("api/auth/me/", MeAPIView.as_view(), name="api-me"),
    path("api/auth/admin-check/", AdminRoleCheckAPIView.as_view(), name="api-admin-check"),
    path("api/auth/teacher-check/", TeacherRoleCheckAPIView.as_view(), name="api-teacher-check"),
]

views.py:
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=phone, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid phone or password.")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")

docker-compose.yml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_DB: education_center
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"