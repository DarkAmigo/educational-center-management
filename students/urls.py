from django.urls import path
from .views import students_view

urlpatterns = [
    path("students/", students_view, name="students"),
]