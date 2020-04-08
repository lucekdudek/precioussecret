from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('precioussecret.service.urls')),
    url(r'^', include('precioussecret.client.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
