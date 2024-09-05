from rest_framework.viewsets import ModelViewSet

from airport import models, serializers


class AirplaneTypeViewSet(ModelViewSet):
    queryset = models.AirplaneType.objects.all()
    serializer_class = serializers.AirplaneTypeSerializer


class AirplaneViewSet(ModelViewSet):
    queryset = models.Airplane.objects.all()
    serializer_class = serializers.AirplaneSerializer


class CountryViewSet(ModelViewSet):
    queryset = models.Country.objects.all()
    serializer_class = serializers.CountrySerializer


class CityViewSet(ModelViewSet):
    queryset = models.City.objects.all()
    serializer_class = serializers.CitySerializer


class AirportViewSet(ModelViewSet):
    queryset = models.Airport.objects.all()
    serializer_class = serializers.AirportSerializer


class RouteViewSet(ModelViewSet):
    queryset = models.Route.objects.all()
    serializer_class = serializers.RouteSerializer


class FlightViewSet(ModelViewSet):
    queryset = models.Flight.objects.all()
    serializer_class = serializers.FlightSerializer


class CrewViewSet(ModelViewSet):
    queryset = models.Crew.objects.all()
    serializer_class = serializers.CrewSerializer


class TicketViewSet(ModelViewSet):
    queryset = models.Ticket.objects.all()
    serializer_class = serializers.TicketSerializer


class OrderViewSet(ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer
