from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from usuarios.permissions import IsAdminOrStaff, IoTApiKeyPermission
from .models import Dispositivo
from .serializers import DispositivoSerializer


class DispositivoViewSet(viewsets.ModelViewSet):
    queryset = Dispositivo.objects.select_related('intersection').all()
    serializer_class = DispositivoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tipo', 'estado', 'activo', 'intersection']
    search_fields = ['nombre', 'device_id', 'mac_address']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdminOrStaff()]

    @action(detail=False, methods=['post'], permission_classes=[IoTApiKeyPermission])
    def heartbeat(self, request):
        """
        ESP32 sends a periodic heartbeat so the backend knows it is online.
        Body: { device_id, ip_address?, firmware_version? }
        """
        device_id = request.data.get('device_id')
        if not device_id:
            return Response({'error': 'device_id requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        dispositivo, _ = Dispositivo.objects.get_or_create(
            device_id=device_id,
            defaults={'nombre': device_id, 'tipo': Dispositivo.TipoChoices.ESP32},
        )
        dispositivo.estado = Dispositivo.EstadoChoices.ONLINE
        dispositivo.ultimo_acceso = timezone.now()

        if 'ip_address' in request.data:
            dispositivo.ip_address = request.data['ip_address']
        if 'firmware_version' in request.data:
            dispositivo.firmware_version = request.data['firmware_version']

        dispositivo.save()
        return Response(DispositivoSerializer(dispositivo).data)
