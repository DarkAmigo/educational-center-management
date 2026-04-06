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
