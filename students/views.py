from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Student


@login_required
def students_view(request):
    students = Student.objects.select_related("branch").all()

    return render(request, "students/students.html", {
        "students": students
    })
