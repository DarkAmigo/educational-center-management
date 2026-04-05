from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

from students.models import Student
from lessons.models import Lesson
from users.models import User


@login_required
def dashboard_view(request):
    user = request.user

    context = {}

    if user.role == User.Role.ADMIN:
        branches = user.get_visible_branches()

        context["branches_count"] = branches.count()
        context["students_count"] = Student.objects.filter(branch__in=branches).count()
        context["teachers_count"] = User.objects.filter(
            role=User.Role.TEACHER,
            lessons__subject__branch__in=branches,
        ).distinct().count()

    today = now().date()
    lessons = Lesson.objects.filter(start_datetime__date=today)

    if user.role == User.Role.TEACHER:
        lessons = lessons.filter(teacher=user)
    elif not user.is_superuser:
        lessons = lessons.filter(subject__branch__in=user.get_visible_branches())

    context["lessons"] = lessons

    return render(request, "core/dashboard.html", context)
