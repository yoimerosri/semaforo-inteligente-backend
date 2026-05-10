from rest_framework import serializers
from .models import Dispositivo


class DispositivoSerializer(serializers.ModelSerializer):
    intersection_name = serializers.CharField(source='intersection.name', read_only=True)

    class Meta:
        model = Dispositivo
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
