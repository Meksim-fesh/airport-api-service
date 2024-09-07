from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins

from airport import models, serializers


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = models.AirplaneType.objects.all()
    serializer_class = serializers.AirplaneTypeSerializer


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = models.Airplane.objects.all()
    serializer_class = serializers.AirplaneSerializer


class CountryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = models.Country.objects.all()
    serializer_class = serializers.CountrySerializer


class CityViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = models.City.objects.all()
    serializer_class = serializers.CitySerializer


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = models.Airport.objects.select_related("city__country")

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.AirportListSerializer
        elif self.action == "retrieve":
            return serializers.AirportDetailSerializer

        return serializers.AirportSerializer


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = models.Route.objects.all()
    serializer_class = serializers.RouteSerializer


class FlightViewSet(ModelViewSet):
    queryset = models.Flight.objects.all()
    serializer_class = serializers.FlightSerializer


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = models.Crew.objects.all()
    serializer_class = serializers.CrewSerializer


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer
