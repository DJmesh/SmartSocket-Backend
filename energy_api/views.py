from django.conf import settings
from django.utils import timezone
from django.db.models import Avg
from django.db.models.functions import TruncMinute, TruncHour, TruncDay, TruncMonth

from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

import os
import requests

from .models import EnergyReading
from .serializers import EnergyReadingSerializer


# ════════════════════════════════════════════════════════════════════════
#  CRUD completo (ViewSet)
# ════════════════════════════════════════════════════════════════════════
class EnergyReadingViewSet(viewsets.ModelViewSet):
    """
    /api/energy/   → CRUD + filtros padrão DRF
    """
    queryset = EnergyReading.objects.all().order_by("-created_at")
    serializer_class = EnergyReadingSerializer


# ════════════════════════════════════════════════════════════════════════
#  Helpers de agregação
# ════════════════════════════════════════════════════════════════════════
def _avg_power_queryset(since, trunc_func):
    qs = (
        EnergyReading.objects
        .filter(created_at__gte=since)
        .annotate(ts=trunc_func("created_at"))
        .values("ts")
        .annotate(avg_w=Avg("active_power_w"))
        .order_by("ts")
    )
    return [
        {"ts": x["ts"].isoformat(), "avg_w": round(x["avg_w"], 2)}
        for x in qs
    ]


# ════════════════════════════════════════════════════════════════════════
#  Endpoints analíticos
# ════════════════════════════════════════════════════════════════════════
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


# ════════════════════════════════════════════════════════════════════════
#  Controle de relé no ESP32 via proxy
# ════════════════════════════════════════════════════════════════════════
# Configure o IP do ESP32 em variável de ambiente ou settings.py
ESP_BASE = (
    os.getenv("ESP_IP")                     # export ESP_IP="http://192.168.1.50"
    or getattr(settings, "ESP_IP", None)    # settings.ESP_IP = "http://192.168.1.50"
)
RELAY_ENDPOINT = f"{ESP_BASE}/relay" if ESP_BASE else None


@api_view(["POST"])
def relay_control(request):
    """
    Recebe {"state":"on"} ou {"state":"off"} e encaminha ao ESP32.
    Retorna esp_status e corpo bruto.
    """
    if not RELAY_ENDPOINT:
        return Response(
            {"error": "ESP_IP não configurado."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    state = request.data.get("state")
    if state not in ("on", "off"):
        return Response(
            {"error": "state deve ser 'on' ou 'off'"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        esp_resp = requests.post(RELAY_ENDPOINT, json={"state": state}, timeout=5)
        return Response(
            {
                "esp_status": esp_resp.status_code,
                "esp_body": esp_resp.text,
            },
            status=esp_resp.status_code,
        )
    except requests.RequestException as exc:
        return Response({"error": str(exc)}, status=502)
