from collections import defaultdict, Counter

from rest_framework.authentication import BasicAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from precioussecret.service.models import Secret
from precioussecret.service.serializers import AddSecretSerializer
from precioussecret.service.serializers import AccessSecretSerializer
from precioussecret.service.serializers import StatisticsSerializer


class AddSecretView(generics.CreateAPIView):
    """API endpoint that allows secret to be added.
    """
    authentication_classes = [BasicAuthentication, TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AddSecretSerializer


class AccessSecretView(generics.UpdateAPIView):
    """API endpoint that allows secret to be viewed.
    """
    queryset = Secret.objects.all()
    serializer_class = AccessSecretSerializer
    lookup_field = 'access_name'

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class StatisticsView(generics.GenericAPIView):
    """API endpoint that allows statistics to be viewed.
    """
    authentication_classes = [BasicAuthentication, TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Secret.objects.all()
    serializer_class = StatisticsSerializer

    def get(self, request, *args, **kwargs):
        """Gets statistics data and returns dict with it
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        statistics_data = defaultdict(lambda: Counter({'files': 0, 'links': 0}))
        for element in serializer.data:
            if element and element[1] == 'URL':
                statistics_data[element[0]]['links'] += 1
            elif element and element[1] == 'FILE':
                statistics_data[element[0]]['files'] += 1
        return Response({key: dict(value) for key, value in statistics_data.items()})
