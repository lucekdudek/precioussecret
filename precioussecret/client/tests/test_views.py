from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.test import TestCase

from rest_framework import status

from precioussecret.client.views import AddSecretView
from precioussecret.client.views import SecretDetailsView


class AddSecretViewTest(TestCase):
    """Test module for add secret  view.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='gollum',
            email='gollum@ring.lord',
            password='myprecioussss'
        )
        self.factory = RequestFactory()

    def test_post_anonymous_user(self):
        request = self.factory.post("N/A")
        request.user = AnonymousUser()
        response = AddSecretView.as_view()(request)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_post_authenticated_user(self):
        request = self.factory.post("N/A")
        request.user = self.user
        response = AddSecretView.as_view()(request)
        self.assertEqual(status.HTTP_200_OK, response.status_code)


class SecretDetailsViewTest(TestCase):
    """Test module for secret details view.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.session_middleware = SessionMiddleware()

    def __fill_request_with_session(self, request, access_name=None, access_code=None):
        self.session_middleware.process_request(request)
        if access_name:
            request.session['access_name'] = access_name
        if access_code:
            request.session['access_code'] = access_code
        request.session.save()

    def test_get_context_data_empty_session(self):
        request = self.factory.get("N/A")
        self.__fill_request_with_session(
            request=request
        )
        response = SecretDetailsView.as_view()(request)
        self.assertIsNone(response.context_data.get('access_url'))
        self.assertIsNone(response.context_data.get('access_code'))

    def test_get_context_data_half_empty_session(self):
        access_code_sample = 'DKERLA'
        request = self.factory.get("N/A")
        self.__fill_request_with_session(
            request=request,
            access_code=access_code_sample
        )
        response = SecretDetailsView.as_view()(request)
        self.assertIsNone(response.context_data.get('access_url'))
        self.assertEqual(access_code_sample, response.context_data.get('access_code'))

    def test_get_context_data_complete_session(self):
        access_code_name = 'sa-mp-le'
        access_code_sample = 'SAMPLE'
        request = self.factory.get("N/A")
        self.__fill_request_with_session(
            request=request,
            access_code=access_code_sample,
            access_name=access_code_name
        )
        response = SecretDetailsView.as_view()(request)
        self.assertIn(access_code_name, response.context_data.get('access_url'))
        self.assertEqual(access_code_sample, response.context_data.get('access_code'))
