from django.urls import path
from .views import branches_view

urlpatterns = [
    path("branches/", branches_view, name="branches"),
]