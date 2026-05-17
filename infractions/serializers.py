from rest_framework import serializers
from .models import Infraction

_STATE_LABELS = {'RED': 'Rojo', 'YELLOW': 'Amarillo', 'GREEN': 'Verde'}


class InfractionSerializer(serializers.ModelSerializer):
    road_name                   = serializers.CharField(source='road.name', read_only=True)
    status_display              = serializers.CharField(source='get_status_display', read_only=True)
    traffic_light_state_display = serializers.SerializerMethodField()
    photo_url                   = serializers.SerializerMethodField()

    class Meta:
        model  = Infraction
        fields = [
            'id', 'road', 'road_name',
            'timestamp',
            'traffic_light_state', 'traffic_light_state_display',
            'vehicle_count', 'confidence',
            'photo_url',
            'status', 'status_display',
            'notes',
        ]
        read_only_fields = [
            'id', 'road', 'road_name', 'timestamp',
            'traffic_light_state', 'traffic_light_state_display',
            'vehicle_count', 'confidence', 'photo_url',
            'status_display',
        ]

    def get_traffic_light_state_display(self, obj):
        return _STATE_LABELS.get(obj.traffic_light_state, obj.traffic_light_state)

    def get_photo_url(self, obj):
        if not obj.photo:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.photo.url)
        return obj.photo.url
