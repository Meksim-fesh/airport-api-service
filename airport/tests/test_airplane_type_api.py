from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from airport.models import AirplaneType
from airport.serializers import AirplaneTypeSerializer


AIRPLANE_TYPE_URL = reverse("airport:airplanetype-list")


def sample_airplane_type(name: str = "Test airplane type"):
    return AirplaneType.objects.create(name=name)


class UnauthenticatedAirplaneTypeApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(AIRPLANE_TYPE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTypeApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_airplane_type(self):
        sample_airplane_type("Airplane type 1")
        sample_airplane_type("Airplane type 2")
        sample_airplane_type("Airplane type 3")

        response = self.client.get(AIRPLANE_TYPE_URL)

        airplane_types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(airplane_types, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_forbidden(self):
        payload = {
            "name": "Test name",
        }

        response = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTypeApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane_type(self):
        name = "Test name"
        payload = {
            "name": name,
        }

        response = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        airplane_type = AirplaneType.objects.get(id=response.data["id"])
        self.assertEqual(airplane_type.name, name)

    def test_create_airplane_type_with_same_name_not_allowed(self):
        name = "Test name"
        sample_airplane_type(name)

        payload = {
            "name": name,
        }

        response = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
