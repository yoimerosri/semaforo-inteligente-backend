from rest_framework import serializers
from .models import Sensor


class SensorSerializer(serializers.ModelSerializer):
    road_name = serializers.CharField(source='road.name', read_only=True)

    class Meta:
        model = Sensor
        fields = ('id', 'road', 'road_name', 'vehicle_detected', 'vehicle_count', 'confidence')
