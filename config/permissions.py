from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models import User


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return request.user.role == User.Role.ADMIN
    
class CanManageAttendance(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        return request.user.role in [
            User.Role.ADMIN,
            User.Role.TEACHER,
        ]

    def has_object_permission(self, request, view, obj):

        if request.user.role == User.Role.ADMIN:
            return True

        return obj.lesson.teacher == request.user