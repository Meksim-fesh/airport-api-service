from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport, City, Country
from airport.serializers import AirportDetailSerializer, AirportListSerializer


AIRPORT_URL = reverse("airport:airport-list")


def get_detail_url(airport_id: int):
    return reverse("airport:airport-detail", args=[airport_id,])


def sample_country(name: str = "Test country"):
    return Country.objects.create(name=name)


def sample_city(country: Country, **params):
    defaults = {
        "name": "Test city",
        "country": country,
    }
    defaults.update(params)

    return City.objects.create(**defaults)


def sample_airport(city: City, **params):
    defaults = {
        "name": "Test airport",
        "city": city,
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


class UnauthenticatedAirportApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(AIRPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_airport(self):
        country = sample_country()
        city_1 = sample_city(country)
        city_2 = sample_city(country)

        sample_airport(city_1)
        sample_airport(city_2)

        airports = Airport.objects.all()
        serializer = AirportListSerializer(airports, many=True)

        response = self.client.get(AIRPORT_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_airports_by_city(self):
        country = sample_country()
        city_1 = sample_city(country, name="City 1")
        city_2 = sample_city(country, name="City 2")
        city_3 = sample_city(country, name="City 3")

        sample_airport(city_1, name="Airport 1")
        sample_airport(city_2, name="Airport 2")
        sample_airport(city_3, name="Airport 3")

        response = self.client.get(
            AIRPORT_URL,
            {"cities": f"{city_1.id},{city_2.id}"}
        )

        airports = Airport.objects.filter(city__id__in=[city_1.id, city_2.id])
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_airports_by_country(self):
        country_1 = sample_country("Country 1")
        country_2 = sample_country("Country 2")
        country_3 = sample_country("Country 3")
        city_1 = sample_city(country_1, name="City 1")
        city_2 = sample_city(country_2, name="City 2")
        city_3 = sample_city(country_3, name="City 3")

        sample_airport(city_1, name="Airport 1")
        sample_airport(city_2, name="Airport 2")
        sample_airport(city_3, name="Airport 3")

        response = self.client.get(
            AIRPORT_URL,
            {"countries": f"{country_1.id},{country_3.id}"}
        )

        airports = Airport.objects.filter(
            city__country__id__in=[country_1.id, country_3.id]
        )
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_airports_by_name(self):
        airport_name = "airport"

        country = sample_country()
        city_1 = sample_city(country)
        city_2 = sample_city(country)
        city_3 = sample_city(country)

        sample_airport(city_1, name="National airport")
        sample_airport(city_2, name="Airport name")
        sample_airport(city_3, name="National name")

        response = self.client.get(
            AIRPORT_URL,
            {"airport_name": airport_name},
        )

        airports = Airport.objects.filter(
            name__icontains=airport_name
        )
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_airport(self):
        country = sample_country()
        city = sample_city(country)

        airport = sample_airport(city)
        serializer = AirportDetailSerializer(airport)

        url = get_detail_url(airport.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_airport_forbidden(self):
        country = sample_country()
        city = sample_city(country)

        payload = {
            "name": "Test airport",
            "city": city,
        }

        response = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_airport(self):
        country = sample_country()
        city = sample_city(country)

        payload = {
            "name": "Test airport",
            "city": city.id,
        }

        response = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        airport = Airport.objects.get(id=response.data["id"])
        self.assertEqual(city, getattr(airport, "city"))
        self.assertEqual("Test airport", getattr(airport, "name"))
