from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport import models


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "capacity",
        )


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.CharField(
        read_only=True, source="airplane_type.name",
    )


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = (
            "id",
            "name",
        )


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.City
        fields = (
            "id",
            "name",
            "country",
        )


class CityListSerializer(CitySerializer):
    country = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name",
    )

    class Meta:
        model = models.City
        fields = (
            "id",
            "name",
            "country",
        )


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Airport
        fields = (
            "id",
            "name",
            "city",
        )


class AirportListSerializer(AirportSerializer):
    city = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name",
    )

    class Meta:
        model = models.Airport
        fields = (
            "id",
            "name",
            "city",
        )


class AirportDetailSerializer(AirportSerializer):
    city = serializers.CharField(read_only=True, source="city.name")
    country = serializers.CharField(read_only=True, source="city.country.name")

    class Meta:
        model = models.Airport
        fields = (
            "id",
            "name",
            "city",
            "country",
        )


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Route
        fields = (
            "id",
            "source",
            "destination",
            "distance",
        )


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(read_only=True, source="source.name")
    destination = serializers.CharField(
        read_only=True, source="destination.name"
    )

    class Meta:
        model = models.Route
        fields = ("id", "source", "destination",)


class RouteDetailSerializer(RouteSerializer):
    source = AirportDetailSerializer(many=False, read_only=True)
    destination = AirportDetailSerializer(many=False, read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Crew
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
        )


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
        )


class FlightListSerializer(FlightSerializer):
    source = serializers.CharField(source="route.source", read_only=True)
    destination = serializers.CharField(
        source="route.destination", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Flight
        fields = (
            "id",
            "source",
            "destination",
            "departure_time",
            "arrival_time",
            "tickets_available",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        models.Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError,
        )
        return data

    class Meta:
        model = models.Ticket
        fields = (
            "id",
            "row",
            "seat",
            "flight",
        )


class TicketSeatSerializer(TicketSerializer):
    class Meta:
        model = models.Ticket
        fields = ("row", "seat",)


class FlightDetailSerializer(FlightSerializer):
    route = RouteDetailSerializer(many=False, read_only=True)
    airplane = AirplaneListSerializer(many=False, read_only=True)
    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )
    taken_seats = TicketSeatSerializer(
        source="tickets", many=True, read_only=True
    )

    class Meta:
        model = models.Flight
        fields = (
            "id",
            "route",
            "departure_time",
            "arrival_time",
            "airplane",
            "crew",
            "taken_seats",
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False, read_only=False)

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = models.Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                models.Ticket.objects.create(order=order, **ticket_data)
            return order

    class Meta:
        model = models.Order
        fields = (
            "id",
            "created_at",
            "tickets",
        )


class OrderListSerializer(OrderSerializer):
    pass
