import random
import string
import uuid

from django.db import models


class Resource(models.Model):
    url = models.URLField(blank=True, null=True)
    file = models.FileField(blank=True, null=True)


def generate_access_name():
    """Returns random uuid.
    """
    return str(uuid.uuid4())


def generate_access_code():
    """Returns short code, Note this code is not necessarily unique.
    """
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(6))


class Secret(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    resource = models.ForeignKey(Resource, on_delete=models.PROTECT)
    access_name = models.CharField(max_length=255, unique=True, db_index=True, default=generate_access_name)
    access_code = models.CharField(max_length=255, default=generate_access_code)
    number_of_accesses = models.IntegerField(default=0)
