from django.urls import include, path
from rest_framework import routers

from airport.views import AirplaneTypeViewSet, AirplaneViewSet, AirportViewSet, CityViewSet, CountryViewSet


router = routers.DefaultRouter()
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("countries", CountryViewSet)
router.register("cities", CityViewSet)
router.register("airports", AirportViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"
