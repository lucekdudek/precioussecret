from rest_framework import status
from rest_framework.exceptions import APIException


class GoneValidationError(APIException):
    status_code = status.HTTP_410_GONE

    def __init__(self, detail):
        self.detail = {'detail': detail}
