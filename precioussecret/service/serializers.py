import base64
import magic
import mimetypes
import uuid

from datetime import timedelta

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.translation import ugettext as _

from rest_framework import serializers

from precioussecret.service.exceptions import GoneValidationError
from precioussecret.service.models import Secret, Resource


class ResourceFileField(serializers.FileField):
    """Custom serializers.FileField responsible for serializing files sent as base64.
    """

    def to_representation(self, value):
        """Gets a file and returns its base64 representation.
        """
        if value:
            return value.url

    def to_internal_value(self, data):
        """Save file received as base64 and returns path to it.
        """
        try:  # ToDo penetrate in order test if it has any security flaws
            decoded = base64.b64decode(data)
            mime_type = magic.from_buffer(decoded, mime=True)
            file_ext = mimetypes.guess_extension(mime_type)
        except TypeError:
            raise serializers.ValidationError(
                _('Not a valid base64 file')
            )

        if file_ext not in settings.VALID_FILE_EXTENSIONS:
            raise serializers.ValidationError(
                _('Invalid file extension')
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

    def to_representation(self, instance):
        """Returns url representation of resource.
        """
        representation = super(ResourceSerializer, self).to_representation(instance)
        url = representation.get('url')
        if url:
            return url

        file = representation.get('file')
        if file:
            return file


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


class AccessSecretSerializer(serializers.Serializer):
    resource = ResourceSerializer(read_only=True)
    access_code = serializers.CharField(write_only=True, required=True)

    def update(self, instance, validated_data):
        """Update and return 'Secret' instance, given the validated data.
        """
        if instance.access_code != validated_data.get('access_code'):
            raise serializers.ValidationError(
                _("Wrong access code"),
            )

        if timezone.now() - instance.created > timedelta(hours=24):
            raise GoneValidationError(
                _("Secret is no longer available"),
            )

        instance.number_of_accesses += 1
        instance.save()
        return instance


class StatisticsSerializer(serializers.Serializer):
    created = serializers.DateTimeField(read_only=True)
    resource = serializers.StringRelatedField(read_only=True)
    number_of_accesses = serializers.IntegerField(read_only=True)

    def to_representation(self, instance):
        """Returns representation for statistics purpose.
        Output format: ('DATE', 'RESOURCE_TYPE') e.g. ('2020-04-08', 'FILE')
        """
        representation = super(StatisticsSerializer, self).to_representation(instance)
        if representation.get('number_of_accesses') > 0:
            return representation.get('created')[:10], representation.get('resource')
        return ()
