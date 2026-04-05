from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

from branches.models import Branch
from students.models import Student
from lessons.models import Lesson
from users.models import User


@login_required
def dashboard_view(request):
    user = request.user

    context = {}

    if user.role == User.Role.ADMIN:
        context["branches_count"] = Branch.objects.count()
        context["students_count"] = Student.objects.count()
        context["teachers_count"] = User.objects.filter(role=User.Role.TEACHER).count()

    today = now().date()
    lessons = Lesson.objects.filter(start_datetime__date=today)

    if user.role == User.Role.TEACHER:
        lessons = lessons.filter(teacher=user)

    context["lessons"] = lessons

    return render(request, "core/dashboard.html", context)