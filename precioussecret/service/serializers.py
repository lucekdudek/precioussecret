import base64
import uuid

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import serializers

from precioussecret.service.models import Secret, Resource


class ResourceFileField(serializers.FileField):
    """Custom serializers.FileField responsible for serializing files sent as base64.
    """

    def to_representation(self, value):
        """Gets a file and returns its base64 representation.
        """
        if value:
            data = default_storage.open(value.path).read()
            encoded=base64.b64encode(data).decode("utf-8")
            return encoded

    def to_internal_value(self, data):
        """Save file received as base64 and returns path to it.
        """
        data = ContentFile(base64.b64decode(data), name=str(uuid.uuid4()))
        return data


class ResourceSerializer(serializers.Serializer):
    url = serializers.URLField(required=False)
    file = ResourceFileField(required=False)


class AddSecretSerializer(serializers.Serializer):
    created = serializers.DateTimeField(read_only=True)
    resource = ResourceSerializer(write_only=True)
    access_name = serializers.CharField(read_only=True)
    access_code = serializers.CharField(read_only=True)

    def create(self, validated_data):
        """Create and return 'Secret' instance, given the validated data.
        """
        resource = Resource.objects.create(**validated_data.get("resource"))
        return Secret.objects.create(resource=resource)
