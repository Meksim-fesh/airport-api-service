from rest_framework import serializers

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


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Airport
        fields = (
            "id",
            "name",
            "city",
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


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ticket
        fields = (
            "id",
            "row",
            "seat",
            "flight",
            "order",
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = (
            "id",
            "created_at",
            "user",
        )
