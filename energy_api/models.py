from django.db import models


class EnergyReading(models.Model):
    """
    Leitura pontual do sensor de energia (EmonLib + ESP32).
    """
    device_id          = models.CharField(max_length=32, default="esp32")
    timestamp_ms       = models.BigIntegerField()
    voltage_v          = models.FloatField()
    current_a          = models.FloatField()
    active_power_w     = models.FloatField()
    apparent_power_va  = models.FloatField()
    reactive_power_var = models.FloatField()
    created_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.device_id} @ {self.created_at:%Y-%m-%d %H:%M:%S}"
