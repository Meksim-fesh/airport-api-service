from django.urls import include, path
from rest_framework import routers

from airport.views import AirplaneTypeViewSet, AirplaneViewSet


router = routers.DefaultRouter()
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"
