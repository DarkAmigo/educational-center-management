from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers


class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        phone = attrs.get("phone")
        password = attrs.get("password")

        if not phone or not password:
            raise serializers.ValidationError("Phone and password required")

        user = authenticate(
            request=self.context.get("request"),
            phone=phone,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }