from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from django.db.models import F, Count

from airport import models, serializers


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class FlightPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100


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
    queryset = models.Airplane.objects.select_related("airplane_type")

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.AirplaneListSerializer
        return serializers.AirplaneSerializer


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
    queryset = models.City.objects.select_related("country")

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.CityListSerializer
        return serializers.CitySerializer


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
    queryset = models.Route.objects.prefetch_related("source", "destination")

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "retrieve":
            queryset = models.Route.objects.select_related(
                "source__city__country", "destination__city__country"
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.RouteListSerializer
        if self.action == "retrieve":
            return serializers.RouteDetailSerializer
        return serializers.RouteSerializer


class FlightViewSet(ModelViewSet):
    queryset = models.Flight.objects.all().annotate(
        tickets_available=(
            F("airplane__rows") * F("airplane__seats_in_row")
            - Count("tickets")
        )
    )
    pagination_class = FlightPagination

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.select_related(
                "route__source__city", "route__destination__city",
            )
        if self.action == "retrieve":
            queryset = queryset.select_related(
                "route__source__city__country",
                "route__destination__city__country",
                "airplane__airplane_type",
            ).prefetch_related("crew", "tickets",)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.FlightListSerializer
        elif self.action == "retrieve":
            return serializers.FlightDetailSerializer
        return serializers.FlightSerializer


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
    permission_classes = (IsAuthenticated, )
    pagination_class = OrderPagination

    def get_queryset(self):
        return models.Order.objects.filter(
            user=self.request.user
        ).prefetch_related(
            "tickets__flight__route__destination",
            "tickets__flight__route__source"
        )

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.OrderListSerializer
        return serializers.OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
