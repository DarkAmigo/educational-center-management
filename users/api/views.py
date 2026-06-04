from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import PhoneTokenObtainPairSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(
    request=PhoneTokenObtainPairSerializer,
    responses=PhoneTokenObtainPairSerializer
)

class PhoneTokenObtainPairView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer