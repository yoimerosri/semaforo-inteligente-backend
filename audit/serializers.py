from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    evento_display = serializers.CharField(source='get_evento_display', read_only=True)

    class Meta:
        model  = AuditLog
        fields = [
            'id', 'evento', 'evento_display',
            'usuario_str', 'ip', 'descripcion',
            'timestamp', 'extra',
        ]
