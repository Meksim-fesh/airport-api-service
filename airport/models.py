from django.db import models
from django.conf import settings


class AirplaneType(models.Model):
    name = models.CharField(unique=True, max_length=255)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.airplane_type})"


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(
        Country,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.country})"


class Airport(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(
        City,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self) -> str:
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        null=True,
        on_delete=models.CASCADE,
        related_name="source_routes",
    )
    destination = models.ForeignKey(
        Airport,
        null=True,
        on_delete=models.CASCADE,
        related_name="destination_routes",
    )
    distance = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.source} - {self.destination}"


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    crew = models.ManyToManyField(Crew)
    route = models.ForeignKey(
        Route,
        null=True,
        on_delete=models.CASCADE,
        related_name="routes",
    )
    airplane = models.ForeignKey(
        Airplane,
        null=True,
        on_delete=models.CASCADE,
        related_name="airplanes",
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.route} ({self.departure_time})"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="flights",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
    )
