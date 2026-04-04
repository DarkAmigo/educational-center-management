from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import User
from .models import Branch


@login_required
def branches_view(request):
    if request.user.role != User.Role.ADMIN:
        return redirect("dashboard")

    branches = Branch.objects.all()

    return render(request, "branches/branches.html", {
        "branches": branches
    })