from django.contrib import admin
from precioussecret.service.models import Resource, Secret

@admin.register(Resource, Secret)
class SecretAdmin(admin.ModelAdmin):
    pass
