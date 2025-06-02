from rest_framework import serializers
from .models import EnergyReading


class EnergyReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EnergyReading
        fields = "__all__"
