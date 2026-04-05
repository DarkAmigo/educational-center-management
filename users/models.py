from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from branches.models import Branch

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Phone must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        TEACHER = 'TEACHER', 'Teacher'

    phone = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=Role.choices)
    assigned_branches = models.ManyToManyField(Branch, blank=True, related_name='assigned_users')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    objects = UserManager()

    def get_visible_branches(self):
        if self.is_superuser:
            return Branch.objects.all()

        if self.role == self.Role.ADMIN:
            return self.assigned_branches.all()

        return Branch.objects.none()

    def can_access_branch(self, branch_id):
        if self.is_superuser:
            return True

        if self.role != self.Role.ADMIN:
            return False

        return self.assigned_branches.filter(pk=branch_id).exists()

    def __str__(self):
        return f"{self.phone} ({self.role})"
