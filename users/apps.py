from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_custom_superuser(sender, **kwargs):
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
        print("=== SUPERUSER CREATED VIA POST_MIGRATE SIGNAL ===")


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        post_migrate.connect(create_custom_superuser, sender=self)