import base64
import magic
import mimetypes
import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.translation import ugettext as _

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
        try:  # ToDo penetrate in order test if it has any security flaws
            decoded = base64.b64decode(data)
            mime_type = magic.from_buffer(decoded, mime=True)
            file_ext = mimetypes.guess_extension(mime_type)
        except TypeError:
            raise serializers.ValidationError(
                _('Not a valid file')
            )

        if file_ext not in settings.VALID_FILE_EXTENSIONS:
            raise serializers.ValidationError(
                _('Invalid file type')
            )

        file_name = "{0}{1}".format(uuid.uuid4(), file_ext)
        data = ContentFile(decoded, name=file_name)
        return data


class ResourceSerializer(serializers.Serializer):
    url = serializers.URLField(required=False)
    file = ResourceFileField(required=False)

    def validate(self, attrs):
        if len(attrs.keys()) != 1:
            raise serializers.ValidationError(
                _("`resource` has to contain exactly one of field"),
            )
        return super(ResourceSerializer, self).validate(attrs)


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
