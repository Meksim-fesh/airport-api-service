from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from airport import models
from airport.serializers import OrderListSerializer


ORDER_URL = reverse("airport:order-list")


def sample_flight(airplane_type, country, *params):
    city_1 = models.City.objects.create(
        name="Test city",
        country=country,
    )
    city_2 = models.City.objects.create(
        name="Test city",
        country=country,
    )
    airport_1 = models.Airport.objects.create(
        name="Test airport",
        city=city_1,
    )
    airport_2 = models.Airport.objects.create(
        name="Test airport",
        city=city_2,
    )

    route = models.Route.objects.create(
        source=airport_1,
        destination=airport_2,
        distance=1234,
    )
    airplane = models.Airplane.objects.create(
        name="Test airplane",
        airplane_type=airplane_type,
        rows=120,
        seats_in_row=6,
    )

    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": "2024-09-01 12:00:00",
        "arrival_time": "2024-09-02 12:00:00",
    }
    defaults.update(params)

    return models.Flight.objects.create(**defaults)


def sample_ticket(flight: int, row: int, seat: int, order: int):
    return models.Ticket.objects.create(
        flight=flight,
        row=row,
        seat=seat,
        order=order,
    )


def sample_order(tickets_data: list[list[int]], user):
    order = models.Order.objects.create(
        user=user,
    )
    for ticket in tickets_data:
        sample_ticket(*ticket, order)

    return order


class UnauthenticatedOrderApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(ORDER_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTest(TestCase):
    def setUp(self) -> None:
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
        self.flight = sample_flight(self.airplane_type, self.country)

    def test_list_order(self):
        sample_order(
            [
                [self.flight, 1, 1,]
            ],
            self.user
        )
        sample_order(
            [
                [self.flight, 2, 2,],
                [self.flight, 3, 3,],
            ],
            self.user
        )

        response = self.client.get(ORDER_URL)

        orders = models.Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_create_order(self):
        payload = {
            "tickets": [
                {
                    "flight": self.flight.id,
                    "row": 1,
                    "seat": 1,
                },
                {
                    "flight": self.flight.id,
                    "row": 2,
                    "seat": 2,
                },
            ]
        }

        response = self.client.post(ORDER_URL, payload, format="json")
        order = models.Order.objects.get(id=response.data["id"])
        tickets = order.tickets.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tickets.count(), 2)
        for ticket in tickets:
            self.assertEqual(self.flight, getattr(ticket, "flight"))

    def test_create_order_with_wrong_row(self):
        payload = {
            "tickets": [
                {
                    "flight": self.flight.id,
                    "row": -1,
                    "seat": 1,
                },
            ]
        }

        response = self.client.post(ORDER_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_wrong_seat(self):
        payload = {
            "tickets": [
                {
                    "flight": self.flight.id,
                    "row": 1,
                    "seat": -1,
                },
            ]
        }

        response = self.client.post(ORDER_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_same_tickets(self):
        payload = {
            "tickets": [
                {
                    "flight": self.flight.id,
                    "row": 1,
                    "seat": 1,
                },
                {
                    "flight": self.flight.id,
                    "row": 1,
                    "seat": 1,
                }
            ]
        }

        response = self.client.post(ORDER_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
