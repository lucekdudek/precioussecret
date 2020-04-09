import base64
import io
import mimetypes

import magic
import requests

from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views import generic

from rest_framework import status
from rest_framework.authtoken.models import Token

from precioussecret.client.forms import AddSecretForm
from precioussecret.client.forms import AccessSecretForm


class LoginView(generic.FormView):
    template_name = 'login.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        return reverse('client:home')


class LogoutView(generic.RedirectView):

    def get(self, request, *args, **kwargs):
        logout(self.request)
        return HttpResponseRedirect(reverse('client:login'))


class HomeView(generic.TemplateView):
    template_name = 'index.html'


class AddSecretView(generic.FormView):
    template_name = 'add-secret.html'
    form_class = AddSecretForm

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        form = self.get_form()
        if not form.is_valid():
            return self.form_invalid(form)

        try:
            resource_dict = self.__prepare_resource_dict(form)
            auth_token, created = Token.objects.get_or_create(user=request.user)
            access_name, access_code = self.__post_secret_to_api(resource_dict, auth_token)
        except ValidationError as e:
            form.add_error(field=None, error=e)
            return self.form_invalid(form)

        request.session['access_name'] = access_name
        request.session['access_code'] = access_code
        return self.form_valid(form)

    def __prepare_resource_dict(self, form):
        """Returns 'resource' based on uploaded data.
        """
        resource_dict = {}

        uploaded_file = form.files.get('file')
        if uploaded_file:
            try:
                file_b64 = base64.b64encode(uploaded_file.file.read()).decode('utf-8')
            except ValueError:
                raise ValidationError(
                    _('Uploaded file is corrupted'),
                    code='corrupted-uploaded-file',
                )
            resource_dict['file'] = file_b64

        uploaded_url = form.data.get('url')
        if uploaded_url:
            resource_dict['url'] = uploaded_url

        if not resource_dict:
            raise ValidationError(
                _('Resource not provided'),
                code='resource-not-provided',
            )

        if all(k in resource_dict for k in ('file', 'url')):
            raise ValidationError(
                _('Resource cannot contain both, url and file.'),
                code='resource-cannot-provide-file-and-url',
            )

        return resource_dict

    def __post_secret_to_api(self, resource_dict, user_token):
        """Send request to API and returns tuple with secret access data.
        """
        response = requests.post(
            self.request.build_absolute_uri(reverse('service:add-secret-endpoint')),
            json={
                'resource': resource_dict
            },
            headers={
                'Content-type': 'application/json',
                'Authorization': 'Token {token}'.format(token=user_token)
            }
        )
        if response.status_code != status.HTTP_201_CREATED:
            raise ValidationError(
                _('Unable to add secret: %(value)s'),
                code='api-secret-not-created',
                params={'value': response.text},
            )

        access_name = response.json().get('access_name')
        access_code = response.json().get('access_code')
        if not all([access_name, access_code]):
            raise ValidationError(
                _('Unable to fetch secret access data'),
                code='api-missing-access-data'
            )
        return access_name, access_code

    def get_success_url(self):
        return reverse('client:secret-details')


class SecretDetailsView(generic.TemplateView):
    template_name = 'secret-details.html'

    def get_context_data(self, **kwargs):
        context = super(SecretDetailsView, self).get_context_data(**kwargs)
        context['access_url'] = self.__get_access_secret_url(self.request.session.get('access_name', None))
        context['access_code'] = self.request.session.get('access_code', None)
        return context

    def __get_access_secret_url(self, access_name):
        """Return access secret url if `access_name` is given.
        """
        if access_name:
            return self.request.build_absolute_uri(
                reverse('client:access-secret', kwargs={'access_name': access_name})
            )


class AccessSecretView(generic.FormView):
    template_name = 'access-secret.html'
    form_class = AccessSecretForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            return self.form_invalid(form)

        try:
            secret_data = self.__access_secret_via_api(kwargs.get('access_name'), form.data.get('access_code'))
        except ValidationError as e:
            form.add_error(field=None, error=e)
            return self.form_invalid(form)

        url = secret_data.get('resource').get('url')
        if url:
            return HttpResponseRedirect(url)

        file_data = secret_data.get('resource').get('file')
        if file_data:
            decoded = base64.b64decode(file_data)
            file = io.BytesIO(decoded)
            mime = magic.from_buffer(decoded, mime=True)
            file_ext = mimetypes.guess_extension(mime)
            response = HttpResponse(file.read(), content_type=mime)
            response['Content-Disposition'] = 'inline; filename={}{}'.format(kwargs.get('access_name'), file_ext)
            return response

        raise Http404(_('Cannot access the secret'))

    def __access_secret_via_api(self, access_name, access_code):
        """Send request to API and returns secret
        """
        response = requests.put(
            self.request.build_absolute_uri(reverse('service:access-secret-endpoint', kwargs={'access_name': access_name})),
            json={
                'access_code': access_code
            },
            headers={
                'Content-type': 'application/json'
            }
        )
        if response.status_code != status.HTTP_200_OK:
            raise ValidationError(
                _('Unable to access secret: %(value)s'),
                code='api-secret-not-accessible',
                params={'value': response.text},
            )

        secret_data = response.json()
        if not secret_data:
            raise ValidationError(
                _('Unable to fetch secret data'),
                code='api-missing-secret-data'
            )
        return secret_data

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form.
        """
        return str(self.success_url)
