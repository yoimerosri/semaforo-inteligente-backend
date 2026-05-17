import logging

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.permissions import IoTApiKeyPermission
from semaforo.models import Road
from .models import Sensor
from .serializers import SensorSerializer

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IoTApiKeyPermission])
def update_sensor(request):
    """
    Recibe el estado del sensor desde ESP32 o el módulo de visión.

    Payload esperado:
        road_id          (int,   requerido)
        vehicle_detected (bool,  requerido)
        vehicle_count    (int,   opcional, default 0)
        confidence       (float, opcional, default 0.0)

    El post_save del modelo Sensor dispara:
        - control_traffic() → actualiza estados de semáforos
        - TrafficRecord.create() → registra evento en historial

    Nota: las infracciones ya NO se crean aquí — se crean en
    /api/infractions/report/ cuando el módulo de visión detecta
    un cruce real de la línea virtual.
    """
    road_id  = request.data.get('road_id')
    detected = request.data.get('vehicle_detected')

    if road_id is None or detected is None:
        logger.warning(
            "Payload incompleto desde %s: road_id=%s vehicle_detected=%s",
            request.META.get('REMOTE_ADDR', '?'), road_id, detected,
        )
        return Response(
            {'error': 'road_id y vehicle_detected son requeridos.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        road_id = int(road_id)
    except (TypeError, ValueError):
        return Response(
            {'error': 'road_id debe ser un entero.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        road = Road.objects.get(id=road_id)
    except Road.DoesNotExist:
        logger.warning("road_id=%d no existe.", road_id)
        return Response(
            {'error': f'road_id={road_id} no existe.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    vehicle_count = int(request.data.get('vehicle_count', 0))
    confidence    = float(request.data.get('confidence', 0.0))

    sensor, _ = Sensor.objects.get_or_create(road=road)
    sensor.vehicle_detected = bool(detected)
    sensor.vehicle_count    = max(0, vehicle_count)
    sensor.confidence       = round(max(0.0, min(1.0, confidence)), 3)
    sensor.save()

    status_str = "DETECTADO" if sensor.vehicle_detected else "AUSENTE"
    logger.info(
        "[SENSOR] via=%-25s  estado=%-9s  count=%d  conf=%.2f",
        road.name, status_str, sensor.vehicle_count, sensor.confidence,
    )

    return Response({
        'status':    'ok',
        'road':      road.name,
        'detected':  sensor.vehicle_detected,
        'count':     sensor.vehicle_count,
        'confidence': sensor.confidence,
    })


class SensorViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only endpoint para que el frontend vea el estado actual de los sensores."""
    queryset         = Sensor.objects.select_related('road').all()
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated]
