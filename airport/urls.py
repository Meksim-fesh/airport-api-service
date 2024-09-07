from django.urls import include, path
from rest_framework import routers

from airport import views


router = routers.DefaultRouter()
router.register("airplane-types", views.AirplaneTypeViewSet)
router.register("airplanes", views.AirplaneViewSet)
router.register("countries", views.CountryViewSet)
router.register("cities", views.CityViewSet)
router.register("airports", views.AirportViewSet)
router.register("routes", views.RouteViewSet)
router.register("crews", views.CrewViewSet)
router.register("flights", views.FlightViewSet)
router.register("orders", views.OrderViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"
