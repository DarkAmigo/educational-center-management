from django.contrib.auth.backends import BaseBackend
from .models import User


class PhoneBackend(BaseBackend):

    def authenticate(self, request, phone=None, password=None):
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None