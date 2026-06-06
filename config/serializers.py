from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class CleanModelSerializer(serializers.ModelSerializer):

    def validate(self, attrs):

        model_class = self.Meta.model

        data = {}

        if self.instance:
            for field in model_class._meta.fields:
                if field.primary_key:
                    continue
                data[field.name] = getattr(self.instance, field.name)

        data.update(attrs)

        model_fields = {
            field.name
            for field in model_class._meta.fields
        }

        filtered_data = {
            key: value
            for key, value in data.items()
            if key in model_fields
        }

        obj = model_class(**filtered_data)

        if self.instance:
            obj.pk = self.instance.pk
            obj._state.adding = False

        try:
            obj.full_clean()

        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs
