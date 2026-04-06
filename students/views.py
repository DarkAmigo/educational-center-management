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
