from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import F, Count

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

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

    @staticmethod
    def _params_to_ints(params) -> list[int]:
        return [int(id_str) for id_str in params.split(",")]

    def _filter_by_location(self, queryset):
        city_ids_str = self.request.query_params.get("cities")
        country_ids_str = self.request.query_params.get("countries")

        if city_ids_str:
            city_ids = self._params_to_ints(city_ids_str)
            queryset = queryset.filter(city__id__in=city_ids)

        if country_ids_str:
            country_ids = self._params_to_ints(country_ids_str)
            queryset = queryset.filter(city__country__id__in=country_ids)

        return queryset

    def _filter_by_name(self, queryset):
        airport_name = self.request.query_params.get("airport_name")

        if airport_name:
            queryset = queryset.filter(name__icontains=airport_name)

        return queryset

    def filter_by_query_params(self, queryset):
        queryset = self._filter_by_location(queryset)
        queryset = self._filter_by_name(queryset)
        return queryset

    def get_queryset(self):
        queryset = self.queryset

        queryset = self.filter_by_query_params(queryset)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.AirportListSerializer

        if self.action == "retrieve":
            return serializers.AirportDetailSerializer

        if self.action == "upload_image":
            return serializers.AirportImageSerializer

        return serializers.AirportSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser,]
    )
    def upload_image(self, request, pk=None):
        airport = self.get_object()
        serializer = self.get_serializer(airport, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


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

    def _filter_by_airport(self, queryset):
        source_airport_id_str = self.request.query_params.get("source_airport")
        destination_airport_id_str = self.request.query_params.get(
            "destination_airport"
        )

        if source_airport_id_str:
            queryset = queryset.filter(
                route__source__id=int(source_airport_id_str)
            )

        if destination_airport_id_str:
            queryset = queryset.filter(
                route__destination__id=int(destination_airport_id_str)
            )

        return queryset

    def _filter_by_city(self, queryset):
        source_city_id_str = self.request.query_params.get("source_city")
        destination_city_id_str = self.request.query_params.get(
            "destination_city"
        )

        if source_city_id_str:
            queryset = queryset.filter(
                route__source__city__id=int(source_city_id_str)
            )

        if destination_city_id_str:
            queryset = queryset.filter(
                route__destination__city__id=int(destination_city_id_str)
            )

        return queryset

    def _filter_by_date(self, queryset):
        departure_date = self.request.query_params.get("departure_date")

        if departure_date:
            queryset = queryset.filter(
                departure_time__date__gte=departure_date
            )

        return queryset

    def filter_by_query_params(self, queryset):
        queryset = self._filter_by_airport(queryset)
        queryset = self._filter_by_city(queryset)
        queryset = self._filter_by_date(queryset)

        return queryset

    def get_queryset(self):
        queryset = self.queryset

        queryset = self.filter_by_query_params(queryset)

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

        if self.action == "retrieve":
            return serializers.FlightDetailSerializer

        return serializers.FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="source_airport",
                description="Filter by source airport (ex. ?source_airport=2)",
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="destination_airport",
                description=(
                    "Filter by destinations airport"
                    " (ex. ?destination_airport=1)"
                ),
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="source_city",
                description="Filter by source city (ex. ?source_city=3)",
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="destination_city",
                description=(
                    "Filter by destinations city"
                    " (ex. ?destination_city=4)"
                ),
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="departure_time",
                description=(
                    "Filter by departure time"
                    " (ex. ?departure_time=2020-01-30)"
                ),
                required=False,
                type=OpenApiTypes.DATE,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Returns list of flights"""
        return super().list(request, *args, **kwargs)

    @extend_schema()
    def create(self, request, *args, **kwargs):
        """Creates an instance of flight model"""
        return super().create(request, *args, **kwargs)

    @extend_schema()
    def retrieve(self, request, *args, **kwargs):
        """Returns detailed information about an instance"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema()
    def partial_update(self, request, *args, **kwargs):
        """Updates an instance (doesn't require all fields to be provided)"""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema()
    def update(self, request, *args, **kwargs):
        """Updates an instance (requires all fields to be provided)"""
        return super().update(request, *args, **kwargs)

    @extend_schema()
    def destroy(self, request, *args, **kwargs):
        """Deletes an instance"""
        return super().destroy(request, *args, **kwargs)


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
