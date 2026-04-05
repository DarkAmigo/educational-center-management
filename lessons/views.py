from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Lesson
from users.models import User


@login_required
def schedule_view(request):
    user = request.user

    lessons = Lesson.objects.select_related(
        "teacher", "student", "group", "subject"
    )

    if user.role == User.Role.TEACHER:
        lessons = lessons.filter(teacher=user)

    return render(request, "lessons/schedule.html", {
        "lessons": lessons
    })