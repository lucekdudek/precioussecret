from django.conf.urls import url
from rest_framework.authtoken.views import obtain_auth_token

from precioussecret.service.views import AccessSecretView
from precioussecret.service.views import AddSecretView
from precioussecret.service.views import StatisticsView

app_name = 'service'

urlpatterns = [
    url(r'^token/', obtain_auth_token),
    url(r'^secret/$', AddSecretView.as_view(), name='add-secret-endpoint'),
    url(r'^secret/(?P<access_name>[\w-]+)/$', AccessSecretView.as_view(), name='access-secret-endpoint'),
    url(r'^statistics/$', StatisticsView.as_view(), name='statistics-endpoint'),
]
