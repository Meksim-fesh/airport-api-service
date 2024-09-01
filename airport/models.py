from django.db import models


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
