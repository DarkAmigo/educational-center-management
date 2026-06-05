"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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

from django.contrib.auth import get_user_model
import os

User = get_user_model()

if os.environ.get('DATABASE_URL') and not User.objects.filter(phone='+12025550147').exists():
    User.objects.create_superuser(
        phone='+12025550147',      
        password='K7!mQ2#vL9@xR4',   
        first_name='Admin',
        last_name='Main'
    )
    print("=== SUPERUSER WITH PHONE CREATED SUCCESSFULLY ===")