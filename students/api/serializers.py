from config.serializers import CleanModelSerializer

from students.models import Student


class StudentSerializer(CleanModelSerializer):

    class Meta:
        model = Student
        fields = "__all__"