from django.urls import path
from .views import dashboard_view, home_view

urlpatterns = [
    path("", home_view),
    path("dashboard/", dashboard_view, name="dashboard"),
]