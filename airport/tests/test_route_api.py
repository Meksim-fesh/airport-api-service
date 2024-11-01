from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import (
    Route,
    Airport,
    City,
    Country,
)
from airport.serializers import RouteDetailSerializer, RouteListSerializer


ROUTE_URL = reverse("airport:route-list")


def get_detail_url(route_id: int):
    return reverse("airport:route-detail", args=[route_id])


def sample_city(country: Country, **params):
    defaults = {
        "name": "Test city",
        "country": country,
    }
    defaults.update(params)

    return City.objects.create(**defaults)


def sample_airport(country: Country, city: City = None, **params):
    if not city:
        city = sample_city(country)

    defaults = {
        "name": "Test airport",
        "city": city,
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


def sample_route(
        source_airport: Airport,
        destination_airport: Airport,
        **params,
):
    defaults = {
        "source": source_airport,
        "destination": destination_airport,
        "distance": 1234,
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


class UnauthenticatedRouteApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

        country = Country.objects.create(name="Test country")
        city_1 = sample_city(country)
        city_2 = sample_city(country)

        self.airport_1 = sample_airport(country, city_1)
        self.airport_2 = sample_airport(country, city_2)

    def test_list_route(self):
        sample_route(self.airport_1, self.airport_2)
        sample_route(self.airport_2, self.airport_1)

        response = self.client.get(ROUTE_URL)

        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_route(self):
        route = sample_route(self.airport_1, self.airport_2)

        url = get_detail_url(route.id)
        response = self.client.get(url)

        serializer = RouteDetailSerializer(route)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_route_forbidden(self):
        payload = {
            "source": self.airport_1,
            "destination": self.airport_2,
            "distance": 1234,
        }

        response = self.client.post(ROUTE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

        country = Country.objects.create(name="Test country")
        city_1 = sample_city(country)
        city_2 = sample_city(country)

        self.airport_1 = sample_airport(country, city_1)
        self.airport_2 = sample_airport(country, city_2)

    def test_create_route(self):
        payload = {
            "source": self.airport_1.id,
            "destination": self.airport_2.id,
            "distance": 1234,
        }

        response = self.client.post(ROUTE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        route = Route.objects.get(id=response.data["id"])

        self.assertEqual(self.airport_1, getattr(route, "source"))
        self.assertEqual(self.airport_2, getattr(route, "destination"))
        self.assertEqual(1234, getattr(route, "distance"))
