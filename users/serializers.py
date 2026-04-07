from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()


class BranchInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    city = serializers.CharField()


class UserInfoSerializer(serializers.ModelSerializer):
    accessible_branches = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'phone',
            'first_name',
            'last_name',
            'role',
            'accessible_branches',
        )

    def get_accessible_branches(self, obj):
        branches = obj.get_visible_branches().values('id', 'name', 'city')
        return BranchInfoSerializer(branches, many=True).data


class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': 'Invalid phone or password.',
    }

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserInfoSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
