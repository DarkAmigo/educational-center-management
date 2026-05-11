from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, phone=phone, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid phone or password.")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")
