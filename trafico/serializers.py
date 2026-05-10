from rest_framework import serializers
from .models import TrafficRecord


class TrafficRecordSerializer(serializers.ModelSerializer):
    road_name = serializers.CharField(source='road.name', read_only=True)

    class Meta:
        model = TrafficRecord
        fields = ('id', 'road', 'road_name', 'vehicle_detected', 'timestamp')
