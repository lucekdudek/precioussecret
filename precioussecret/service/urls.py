from django.conf.urls import url

from precioussecret.service.views import AccessSecretView
from precioussecret.service.views import AddSecretView
from precioussecret.service.views import StatisticsView

app_name = 'service'

urlpatterns = [
    url(r'^secret/$', AddSecretView.as_view()),
    url(r'^secret/(?P<access_name>[\w-]+)/$', AccessSecretView.as_view()),
    url(r'^statistics/$', StatisticsView.as_view()),
]
