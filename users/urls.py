from django.urls import path
from .api_views import (
    AdminRoleCheckAPIView,
    LogoutAPIView,
    MeAPIView,
    PhoneLoginAPIView,
    PhoneRefreshAPIView,
    TeacherRoleCheckAPIView,
)
from .views import login_view, logout_view

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("api/auth/login/", PhoneLoginAPIView.as_view(), name="api-login"),
    path("api/auth/refresh/", PhoneRefreshAPIView.as_view(), name="api-refresh"),
    path("api/auth/logout/", LogoutAPIView.as_view(), name="api-logout"),
    path("api/auth/me/", MeAPIView.as_view(), name="api-me"),
    path("api/auth/admin-check/", AdminRoleCheckAPIView.as_view(), name="api-admin-check"),
    path("api/auth/teacher-check/", TeacherRoleCheckAPIView.as_view(), name="api-teacher-check"),
]
