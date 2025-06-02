from django.utils import timezone
from django.db.models import Avg
from django.db.models.functions import (
    TruncMinute, TruncHour, TruncDay, TruncMonth
)
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import EnergyReading
from .serializers import EnergyReadingSerializer


class EnergyReadingViewSet(viewsets.ModelViewSet):
    """
    CRUD para leituras de energia.
    Ex.: POST /api/energy/   (ESP32)
         GET  /api/energy/   (+ filtros padrão DRF)
    """
    queryset = EnergyReading.objects.all().order_by("-created_at")
    serializer_class = EnergyReadingSerializer


# ---------- helpers de agregação ---------- #
def _avg_power_queryset(since, trunc_func):
    """
    Retorna lista [{ts, avg_w}] com média de potência ativa (W)
    ajustada ao intervalo de agregação.
    """
    qs = (EnergyReading.objects
          .filter(created_at__gte=since)
          .annotate(t=trunc_func("created_at"))
          .values("t")
          .annotate(avg_w=Avg("active_power_w"))
          .order_by("t"))
    return [{"ts": x["t"].isoformat(), "avg_w": round(x["avg_w"], 2)}
            for x in qs]


# ---------- endpoints agregados ---------- #
@api_view(["GET"])
def power_last_hour(request):
    since = timezone.now() - timezone.timedelta(hours=1)
    return Response(_avg_power_queryset(since, TruncMinute))


@api_view(["GET"])
def power_last_day(request):
    since = timezone.now() - timezone.timedelta(days=1)
    return Response(_avg_power_queryset(since, TruncHour))


@api_view(["GET"])
def power_last_week(request):
    since = timezone.now() - timezone.timedelta(days=7)
    return Response(_avg_power_queryset(since, TruncDay))


@api_view(["GET"])
def power_last_month(request):
    since = timezone.now() - timezone.timedelta(days=30)
    return Response(_avg_power_queryset(since, TruncDay))


@api_view(["GET"])
def power_year(request):
    year_start = timezone.now().replace(month=1, day=1, hour=0,
                                        minute=0, second=0, microsecond=0)
    return Response(_avg_power_queryset(year_start, TruncMonth))
