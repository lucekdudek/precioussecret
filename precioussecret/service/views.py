from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from precioussecret.service.serializers import AddSecretSerializer


class AddSecretView(APIView):
    """API endpoint that allows secret to be added.
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        url_serializer = AddSecretSerializer(data=request.data)
        if url_serializer.is_valid():
            url_serializer.save()
            return Response(url_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(url_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccessSecretView(APIView):
    """API endpoint that allows secret to be viewed.
    """
    ...


class StatisticsView(APIView):
    """API endpoint that allows statistics to be viewed.
    """
    ...
