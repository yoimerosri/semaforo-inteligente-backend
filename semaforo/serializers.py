from rest_framework import serializers
from .models import Intersection, Road, TrafficLight


class IntersectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intersection
        fields = '__all__'


class RoadSerializer(serializers.ModelSerializer):
    intersection_name = serializers.CharField(source='intersection.name', read_only=True)

    class Meta:
        model = Road
        fields = ('id', 'name', 'is_main', 'intersection', 'intersection_name')


class TrafficLightSerializer(serializers.ModelSerializer):
    road_name = serializers.CharField(source='road.name', read_only=True)
    road_is_main = serializers.BooleanField(source='road.is_main', read_only=True)

    class Meta:
        model = TrafficLight
        fields = ('id', 'road', 'road_name', 'road_is_main', 'state', 'manual_override', 'green_duration', 'updated_at')
        read_only_fields = ('updated_at',)


class TrafficLightControlSerializer(serializers.Serializer):
    """Used by the manual-override endpoint from the frontend."""
    road_id = serializers.IntegerField()
    estado = serializers.ChoiceField(choices=['rojo', 'amarillo', 'verde'])
    manual_override = serializers.BooleanField(default=True)
