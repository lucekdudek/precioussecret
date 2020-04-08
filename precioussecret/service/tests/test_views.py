import shutil

from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.test import TestCase
from django.utils import timezone

from rest_framework import status

from precioussecret.service.models import Resource
from precioussecret.service.models import Secret
from precioussecret.service.views import AddSecretView
from precioussecret.service.views import AccessSecretView
from precioussecret.service.views import StatisticsView


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
        request = self.factory.post('N/A', data=data, content_type='application/json')
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
        request = self.factory.post('N/A', data=data, content_type='application/json')
        request._dont_enforce_csrf_checks = True
        request.user = self.user
        response = AddSecretView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_bad_request(self):
        request = self.factory.post('N/A')
        request._dont_enforce_csrf_checks = True
        request.user = self.user
        response = AddSecretView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized(self):
        request = self.factory.get('N/A')
        response = AddSecretView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_method_not_allowed(self):
        request = self.factory.get('N/A')
        request.user = self.user
        response = AddSecretView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AccessSecretViewTest(TestCase):
    """Test module for adding new secret.
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_access_secret_ok(self):
        secret = Secret.objects.create(
            resource=Resource.objects.create(
                url='https://www.google.com/'
            )
        )
        data = {'access_code': secret.access_code}
        request = self.factory.put('N/A', data=data, content_type='application/json')
        response = AccessSecretView.as_view()(request, **{'access_name': secret.access_name})
        updated_secret = Secret.objects.get(access_name=secret.access_name)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(secret.resource.url, response.data.get('resource'))
        self.assertEqual(secret.number_of_accesses + 1, updated_secret.number_of_accesses)

    def test_access_secret_gone(self):
        secret = Secret.objects.create(
            resource=Resource.objects.create(
                url='https://www.google.com/'
            )
        )
        secret.created = timezone.now() - timedelta(hours=24)
        secret.save()
        data = {'access_code': secret.access_code}
        request = self.factory.put('N/A', data=data, content_type='application/json')
        response = AccessSecretView.as_view()(request, **{'access_name': secret.access_name})
        self.assertEqual(status.HTTP_410_GONE, response.status_code)

    def test_access_secret_wrong_access_name(self):
        secret = Secret.objects.create(
            resource=Resource.objects.create(
                url='https://www.google.com/'
            )
        )
        data = {'access_code': secret.access_code}
        request = self.factory.put('N/A', data=data, content_type='application/json')
        response = AccessSecretView.as_view()(request, **{'access_name': 'fd53c240-2a24-449f-92f4-0f8975c1aad5'})
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_access_secret_wrong_access_code(self):
        secret = Secret.objects.create(
            resource=Resource.objects.create(
                url='https://www.google.com/'
            )
        )
        data = {'access_code': 'SAMPLE'}
        request = self.factory.put('N/A', data=data, content_type='application/json')
        response = AccessSecretView.as_view()(request, **{'access_name': secret.access_name})
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_access_secret_not_found(self):
        data = {'access_code': 'SAMPLE'}
        request = self.factory.put('N/A', data=data, content_type='application/json')
        response = AccessSecretView.as_view()(request, **{'access_name': 'fd53c240-2a24-449f-92f4-0f8975c1aad5'})
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_access_secret_bad_request(self):
        secret = Secret.objects.create(
            resource=Resource.objects.create(
                url='https://www.google.com/'
            )
        )
        data = {}
        request = self.factory.put('N/A', data=data, content_type='application/json')
        response = AccessSecretView.as_view()(request, **{'access_name': secret.access_name})
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_method_get_not_allowed(self):
        request = self.factory.get('N/A')
        response = AccessSecretView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_post_not_allowed(self):
        request = self.factory.post('N/A')
        response = AccessSecretView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_patch_not_allowed(self):
        request = self.factory.patch('N/A')
        response = AccessSecretView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_access_secret_illegal_update(self):
        secret = Secret.objects.create(
            resource=Resource.objects.create(
                url='https://www.google.com/'
            )
        )
        data = {
            'access_code': secret.access_code,
            'number_of_accesses': 100,
            'access_name': 'sample',
            'resource': {'url':'https://www.elgoog.com/'}
        }
        request = self.factory.put('N/A', data=data, content_type='application/json')
        response = AccessSecretView.as_view()(request, **{'access_name': secret.access_name})
        updated_secret = Secret.objects.get(access_name=secret.access_name)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(secret.resource.url, response.data.get('resource'))
        self.assertEqual(secret.number_of_accesses + 1, updated_secret.number_of_accesses)
        self.assertEqual(secret.created, updated_secret.created)
        self.assertEqual(secret.resource.url, updated_secret.resource.url)
        self.assertEqual(secret.access_name, updated_secret.access_name)
        self.assertEqual(secret.access_code, updated_secret.access_code)


class StatisticsViewTest(TestCase):
    """Test module for adding new secret.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='gollum',
            email='gollum@ring.lord',
            password='myprecioussss'
        )
        self.factory = RequestFactory()

    def test_statistics_unauthorized(self):
        request = self.factory.get('N/A')
        response = StatisticsView.as_view()(request)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_statistics_ok(self):
        secret = Secret.objects.create(
            resource=Resource.objects.create(
                url='https://www.google.com/'
            ),
            number_of_accesses=2
        )
        request = self.factory.get('N/A')
        request.user = self.user
        response = StatisticsView.as_view()(request)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn(str(secret.created.date()), response.data)
