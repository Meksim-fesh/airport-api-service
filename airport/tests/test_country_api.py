from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Country
from airport.serializers import CountrySerializer


COUNTRY_URL = reverse("airport:country-list")


def sample_country(name: str = "Test country"):
    return Country.objects.create(name=name)


class UnauthenticatedCountryApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(COUNTRY_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCountryApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_country(self):
        sample_country("Country 1")
        sample_country("Country 2")
        sample_country("Country 3")

        response = self.client.get(COUNTRY_URL)

        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_forbidden(self):
        payload = {
            "name": "Test country",
        }

        response = self.client.post(COUNTRY_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCountryApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_country(self):
        country_name = "Test country name"
        payload = {
            "name": country_name,
        }

        response = self.client.post(COUNTRY_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        country = Country.objects.get(id=response.data["id"])
        self.assertEqual(country_name, country.name)

    def test_create_country_with_same_name_not_allowed(self):
        name = "Same name"
        sample_country(name)

        payload = {
            "name": name,
        }

        response = self.client.post(COUNTRY_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
