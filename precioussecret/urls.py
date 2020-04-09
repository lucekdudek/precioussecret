from django.conf.urls import url
from django.contrib import admin
from django.urls import include

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('precioussecret.service.urls')),
    url(r'^', include('precioussecret.client.urls')),
]
