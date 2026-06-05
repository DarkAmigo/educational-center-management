from django.test import TestCase
from django.urls import reverse

from users.models import User


class UserManagerTests(TestCase):
    user_data = {
        "phone": "+380991112233",
        "password": "StrongPass123",
        "first_name": "Ivan",
        "last_name": "Petrenko",
        "role": User.Role.TEACHER,
    }

    def create_test_user(self, **extra_fields):
        fields = self.user_data.copy()
        fields.update(extra_fields)
        return User.objects.create_user(**fields)

    def login_user(self, user):
        return self.client.post(
            reverse("login"),
            {
                "phone": user.phone,
                "password": self.user_data["password"],
            },
        )

    def test_create_user(self):
        user = self.create_test_user()

        self.assertEqual(user.phone, self.user_data["phone"])
        self.assertEqual(user.first_name, self.user_data["first_name"])
        self.assertEqual(user.last_name, self.user_data["last_name"])
        self.assertEqual(user.role, self.user_data["role"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_login(self):
        user = self.create_test_user()

        response = self.login_user(user)

        self.assertRedirects(response, reverse("dashboard"), fetch_redirect_response=False)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_inactive_user_cannot_login(self):
        user = self.create_test_user(is_active=False)

        response = self.login_user(user)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
