from rest_framework.viewsets import ModelViewSet

from airport.models import Airplane, AirplaneType
from airport.serializers import AirplaneSerializer, AirplaneTypeSerializer


class AirplaneTypeViewSet(ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
