from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .permissions import IsAdminRole, IsTeacherRole
from .serializers import (
    LogoutSerializer,
    PhoneTokenObtainPairSerializer,
    UserInfoSerializer,
)


class PhoneLoginAPIView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = PhoneTokenObtainPairSerializer


class PhoneRefreshAPIView(TokenRefreshView):
    permission_classes = [AllowAny]


class LogoutAPIView(GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
        except TokenError:
            return Response(
                {'detail': 'Invalid refresh token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class MeAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(UserInfoSerializer(request.user).data)


class AdminRoleCheckAPIView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        return Response({'detail': 'Admin access granted.'})


class TeacherRoleCheckAPIView(APIView):
    permission_classes = [IsTeacherRole]

    def get(self, request, *args, **kwargs):
        return Response({'detail': 'Teacher access granted.'})
