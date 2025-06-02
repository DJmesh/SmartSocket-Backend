from django.contrib import admin
from .models import EnergyReading


@admin.register(EnergyReading)
class EnergyReadingAdmin(admin.ModelAdmin):
    list_display  = ("device_id", "created_at", "voltage_v",
                    "current_a", "active_power_w")
    list_filter   = ("device_id", "created_at")
    search_fields = ("device_id",)
