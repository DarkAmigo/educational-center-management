from config.serializers import CleanModelSerializer

from branches.models import (
    Branch,
    Subject,
    Group,
)


class BranchSerializer(CleanModelSerializer):

    class Meta:
        model = Branch
        fields = "__all__"


class SubjectSerializer(CleanModelSerializer):

    class Meta:
        model = Subject
        fields = "__all__"


class GroupSerializer(CleanModelSerializer):

    class Meta:
        model = Group
        fields = "__all__"