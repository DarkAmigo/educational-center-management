from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers

class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):

    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    username_field = "phone"

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserInfoSerializer(self.user).data
        return data