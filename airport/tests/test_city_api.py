from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from airport.models import City, Country
from airport.serializers import CityListSerializer

CITY_URL = reverse("airport:city-list")


def sample_country(name: str = "Test country"):
    return Country.objects.create(name=name)


def sample_city(country: Country, **params):
    defaults = {
        "name": "Test city",
        "country": country,
    }
    defaults.update(params)

    return City.objects.create(**defaults)


class UnauthenticatedCityApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(CITY_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCityApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

        self.country = sample_country()

    def test_list_city(self):
        sample_city(self.country)
        sample_city(self.country)

        response = self.client.get(CITY_URL)

        cities = City.objects.all()
        serializer = CityListSerializer(cities, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_city_forbidden(self):
        payload = {
            "name": "Test city",
            "country": self.country.id,
        }

        response = self.client.post(CITY_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCityApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

        self.country = sample_country()

    def test_create_city(self):
        payload = {
            "name": "Test country",
            "country": self.country.id,
        }

        response = self.client.post(CITY_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        city = City.objects.get(id=response.data["id"])
        self.assertEqual(self.country, city.country)
