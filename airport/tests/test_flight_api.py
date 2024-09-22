from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from airport import models, serializers


FLIGHT_URL = reverse("airport:flight-list")


def get_detail_url(flight_id: int):
    return reverse("airport:flight-detail", args=[flight_id])


def sample_city(country: models.Country, **params):
    defaults = {
        "name": "Test city",
        "country": country,
    }
    defaults.update(params)

    return models.City.objects.create(**defaults)


def sample_airport(
        country: models.Country,
        city: models.City = None,
        **params
):
    if not city:
        city = sample_city(country)

    defaults = {
        "name": "Test airport",
        "city": city,
    }
    defaults.update(params)

    return models.Airport.objects.create(**defaults)


def sample_route(
        source_airport: models.Airport,
        destination_airport: models.Airport,
        **params
):
    defaults = {
        "source": source_airport,
        "destination": destination_airport,
        "distance": 1234,
    }
    defaults.update(params)

    return models.Route.objects.create(**defaults)


def sample_airplane(airplane_type: models.AirplaneType, **params):
    defaults = {
        "name": "Test name",
        "rows": 100,
        "seats_in_row": 6,
        "airplane_type": airplane_type,
    }
    defaults.update(params)

    return models.Airplane.objects.create(**defaults)


def sample_flight(
        route: models.Route,
        airplane: models.Airplane,
        **params
):
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": "2024-09-01 12:00:00",
        "arrival_time": "2024-09-02 12:00:00",
    }
    defaults.update(params)

    return models.Flight.objects.create(**defaults)


def remove_tickets_available_fields(response):
    for flight_data in response.data["results"]:
        flight_data.pop("tickets_available")

    return response


class UnauthenticatedFlightApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

        self.country = models.Country.objects.create(
            name="Test country",
        )
        self.airplane_type = models.AirplaneType.objects.create(
            name="Test airplane type",
        )

        self.airplane = sample_airplane(self.airplane_type)

    def test_list_flight(self):
        airport_1 = sample_airport(self.country)
        airport_2 = sample_airport(self.country)

        route_1 = sample_route(airport_1, airport_2)
        route_2 = sample_route(airport_2, airport_1)

        sample_flight(route_1, self.airplane)
        sample_flight(route_2, self.airplane)

        response = self.client.get(FLIGHT_URL)

        flights = models.Flight.objects.all()
        serializer = serializers.FlightListSerializer(flights, many=True)

        for flight_data in response.data["results"]:
            self.assertIn("tickets_available", flight_data)
            flight_data.pop("tickets_available")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_filter_flights_by_source_and_destination_cities(self):
        city_1 = sample_city(self.country, name="City name 1")
        city_2 = sample_city(self.country, name="City name 2")

        airport_1 = sample_airport(self.country, city_1)
        airport_2 = sample_airport(self.country, city_2)

        route_1 = sample_route(airport_1, airport_2)
        route_2 = sample_route(airport_2, airport_1)

        sample_flight(route_1, self.airplane)
        sample_flight(route_2, self.airplane)

        flight_1 = models.Flight.objects.first()
        flight_2 = models.Flight.objects.last()

        response = self.client.get(
            FLIGHT_URL, {"source_city": city_1.id}
        )

        serializer_1 = serializers.FlightListSerializer(flight_1)
        serializer_2 = serializers.FlightListSerializer(flight_2)

        response = remove_tickets_available_fields(response)

        self.assertIn(serializer_1.data, response.data["results"])
        self.assertNotIn(serializer_2.data, response.data["results"])

        response = self.client.get(
            FLIGHT_URL, {"destination_city": city_1.id}
        )

        response = remove_tickets_available_fields(response)

        self.assertIn(serializer_2.data, response.data["results"])
        self.assertNotIn(serializer_1.data, response.data["results"])

    def test_filter_flights_by_source_and_destination_airports(self):
        airport_1 = sample_airport(self.country, name="Airport 1")
        airport_2 = sample_airport(self.country, name="Airport 2")

        route_1 = sample_route(airport_1, airport_2)
        route_2 = sample_route(airport_2, airport_1)

        sample_flight(route_1, self.airplane)
        sample_flight(route_2, self.airplane)

        flight_1 = models.Flight.objects.first()
        flight_2 = models.Flight.objects.last()

        response = self.client.get(
            FLIGHT_URL, {"source_airport": airport_1.id}
        )

        serializer_1 = serializers.FlightListSerializer(flight_1)
        serializer_2 = serializers.FlightListSerializer(flight_2)

        response = remove_tickets_available_fields(response)

        self.assertIn(serializer_1.data, response.data["results"])
        self.assertNotIn(serializer_2.data, response.data["results"])

        response = self.client.get(
            FLIGHT_URL, {"destination_airport": airport_1.id}
        )

        response = remove_tickets_available_fields(response)

        self.assertIn(serializer_2.data, response.data["results"])
        self.assertNotIn(serializer_1.data, response.data["results"])

    def test_filter_flights_by_departure_date(self):
        airport_1 = sample_airport(self.country)
        airport_2 = sample_airport(self.country)

        route_1 = sample_route(airport_1, airport_2)
        route_2 = sample_route(airport_2, airport_1)

        sample_flight(
            route_1,
            self.airplane,
            departure_time="2024-08-01 12:00:00"
        )
        sample_flight(
            route_2,
            self.airplane,
            departure_time="2024-08-20 12:00:00"
        )

        flight_1 = models.Flight.objects.first()
        flight_2 = models.Flight.objects.last()

        response = self.client.get(
            FLIGHT_URL, {"departure_date": "2024-08-20"}
        )

        response = remove_tickets_available_fields(response)

        serializer_1 = serializers.FlightListSerializer(flight_1)
        serializer_2 = serializers.FlightListSerializer(flight_2)

        self.assertNotIn(serializer_1.data, response.data["results"])
        self.assertIn(serializer_2.data, response.data["results"])

    def test_retrieve_flight_detail(self):
        airport_1 = sample_airport(self.country)
        airport_2 = sample_airport(self.country)

        route = sample_route(airport_1, airport_2)

        sample_flight(route, self.airplane)
        flight = models.Flight.objects.first()

        url = get_detail_url(flight.id)
        response = self.client.get(url)

        serializer = serializers.FlightDetailSerializer(flight)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_flight_forbidden(self):
        airport_1 = sample_airport(self.country)
        airport_2 = sample_airport(self.country)

        route = sample_route(airport_1, airport_2)

        payload = {
            "route": route,
            "airplane": self.airplane,
            "departure_time": "2024-09-01 12:00:00",
            "arrival_time": "2024-09-02 12:00:00",
        }
        response = self.client.post(
            FLIGHT_URL, payload
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
