from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from precioussecret.client.views import AddSecretView
from precioussecret.client.views import AccessSecretView
from precioussecret.client.views import HomeView
from precioussecret.client.views import LoginView
from precioussecret.client.views import SecretDetailsView

app_name = 'client'

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^add-secret/$', login_required(AddSecretView.as_view()), name='add-secret'),
    url(r'^secret-details/$', SecretDetailsView.as_view(), name='secret-details'),
    url(r'^access-secret/(?P<access_name>[\w-]+)/$', AccessSecretView.as_view(), name='access-secret'),
]
