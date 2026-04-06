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
