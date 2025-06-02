from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    EnergyReadingViewSet,
    power_last_hour, power_last_day, power_last_week,
    power_last_month, power_year
)

router = DefaultRouter()
router.register(r"energy", EnergyReadingViewSet, basename="energy")

urlpatterns = [
    path("", include(router.urls)),

    # agregações
    path("stats/power/hour/",  power_last_hour,  name="power-hour"),
    path("stats/power/day/",   power_last_day,   name="power-day"),
    path("stats/power/week/",  power_last_week,  name="power-week"),
    path("stats/power/month/", power_last_month, name="power-month"),
    path("stats/power/year/",  power_year,       name="power-year"),
]
