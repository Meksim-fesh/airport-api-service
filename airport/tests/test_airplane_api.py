from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Airplane, AirplaneType
from airport.serializers import AirplaneListSerializer


AIRPLANE_URL = reverse("airport:airplane-list")


def sample_airplane_type(name: str = "Test airplane type"):
    return AirplaneType.objects.create(name=name)


def sample_airplane(airplane_type: AirplaneType, **params):
    defaults = {
        "name": "Test airplane",
        "rows": 123,
        "seats_in_row": 6,
        "airplane_type": airplane_type,
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


class UnauthenticatedAirplaneApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(AIRPLANE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

        self.airplane_type = sample_airplane_type()

    def test_list_airplane(self):
        sample_airplane(self.airplane_type)
        sample_airplane(self.airplane_type)

        response = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_capacity_shown(self):
        rows = 100
        seats = 5
        capacity = rows * seats

        sample_airplane(self.airplane_type, rows=rows, seats_in_row=seats)
        sample_airplane(self.airplane_type, rows=rows, seats_in_row=seats)

        response = self.client.get(AIRPLANE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for airplane in response.data:
            self.assertEqual(airplane["capacity"], capacity)

    def test_create_forbidden(self):
        payload = {
            "name": "Test airplane naeme",
            "rows": 100,
            "seats_in_row": 5,
            "airplane_type": self.airplane_type.id,
        }

        response = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "testpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.airplane_type = sample_airplane_type()

    def test_create_airplane(self):
        payload = {
            "name": "Test airplane naeme",
            "rows": 100,
            "seats_in_row": 5,
            "airplane_type": self.airplane_type.id,
        }

        response = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        airplane = Airplane.objects.get(id=response.data["id"])
        self.assertEqual(self.airplane_type, airplane.airplane_type)
        self.assertEqual(100, airplane.rows)
        self.assertEqual(5, airplane.seats_in_row)
