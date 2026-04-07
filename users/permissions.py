from rest_framework.permissions import BasePermission

from .models import User


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and (
                user.is_superuser or user.role == User.Role.ADMIN
            )
        )


class IsTeacherRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and (
                user.is_superuser or user.role == User.Role.TEACHER
            )
        )
