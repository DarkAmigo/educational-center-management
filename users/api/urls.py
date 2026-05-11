from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import PhoneTokenObtainPairView

urlpatterns = [
    path("login/", PhoneTokenObtainPairView.as_view(), name="jwt-login"),
    path("refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
]