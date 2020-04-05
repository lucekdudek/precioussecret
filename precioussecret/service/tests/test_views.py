import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.test import TestCase

from rest_framework import status

from precioussecret.service.views import AddSecretView


class AddSecretViewTest(TestCase):
    """Test module for adding new secret.
    """

    settings.MEDIA_ROOT += '_test'

    def setUp(self):
        self.user = User.objects.create_user(
            username='gollum',
            email='gollum@ring.lord',
            password='myprecioussss'
        )
        self.factory = RequestFactory()

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_url_secret_created(self):
        data = {
            "resource":
                {
                    "url":"https://www.google.com/"
                }
        }
        request = self.factory.post('/api/secret/', data=data, content_type='application/json')
        request._dont_enforce_csrf_checks = True
        request.user = self.user
        response = AddSecretView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_file_secret_created(self):
        data = {
            "resource":
                {
                    "file":"iVBORw0KGgoAAAANSUhEUgAAAAMAAAADCAYAAABWKLW/AAAAEklEQVR42mNUaG+vZ4ACRpwcAHTuBQv2OFcqAAAAAElFTkSuQmCC"
                }
        }
        request = self.factory.post('/api/secret/', data=data, content_type='application/json')
        request._dont_enforce_csrf_checks = True
        request.user = self.user
        response = AddSecretView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_bad_request(self):
        request = self.factory.post('/api/secret/')
        request._dont_enforce_csrf_checks = True
        request.user = self.user
        response = AddSecretView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_forbidden(self):
        request = self.factory.get('/api/secret/')
        response = AddSecretView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_method_not_allowed(self):
        request = self.factory.get('/api/secret/')
        request.user = self.user
        response = AddSecretView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
