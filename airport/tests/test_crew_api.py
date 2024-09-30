from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Crew
from airport.serializers import CrewSerializer


CREW_URL = reverse("airport:crew-list")


def sample_crew(**params):
    defaults = {
        "first_name": "First name",
        "last_name": "Last name",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


class UnauthenticatedCrewApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(CREW_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_crew(self):
        sample_crew()
        sample_crew()

        response = self.client.get(CREW_URL)

        crews = Crew.objects.all()
        serializer = CrewSerializer(crews, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_full_name_shown(self):
        full_name = "First Last"
        sample_crew(first_name="First", last_name="Last")
        sample_crew(first_name="First", last_name="Last")

        response = self.client.get(CREW_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for crew in response.data:
            self.assertEqual(crew["full_name"], full_name)

    def test_create_forbidden(self):
        payload = {
            "first_name": "First",
            "last_name": "Last",
        }

        response = self.client.post(CREW_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_crew(self):
        first_name = "First"
        last_name = "Last"
        payload = {
            "first_name": first_name,
            "last_name": last_name,
        }

        response = self.client.post(CREW_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        crew = Crew.objects.get(id=response.data["id"])
        self.assertEqual(crew.first_name, first_name)
        self.assertEqual(crew.last_name, last_name)
