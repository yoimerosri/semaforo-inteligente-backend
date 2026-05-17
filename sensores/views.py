import base64
import logging
import time

from django.core.files.base import ContentFile
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.permissions import IoTApiKeyPermission
from semaforo.models import Road
from .models import Sensor
from .serializers import SensorSerializer

logger = logging.getLogger(__name__)


def _create_infraction(road, vehicle_count, confidence, light_state, photo_b64):
    """Crea una Infraction con foto opcional cuando un vehículo cruza en rojo."""
    from infractions.models import Infraction

    intr = Infraction(
        road=road,
        traffic_light_state=light_state,
        vehicle_count=vehicle_count,
        confidence=round(confidence, 3),
    )

    if photo_b64:
        try:
            img_bytes = base64.b64decode(photo_b64)
            filename  = f"inf_{road.id}_{int(time.time())}.jpg"
            intr.photo.save(filename, ContentFile(img_bytes), save=False)
        except Exception as exc:
            logger.warning("[INFRACCIÓN] No se pudo guardar la foto para via=%s: %s", road.name, exc)

    intr.save()
    logger.warning(
        "[INFRACCIÓN] CREADA — via=%-25s  state=%s  count=%d  conf=%.2f  foto=%s",
        road.name, light_state, vehicle_count, confidence,
        "sí" if intr.photo else "no",
    )


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
        photo            (str,   opcional, base64 JPEG — usado para fotomultas)

    Si vehicle_detected=True y el semáforo de la vía está en ROJO,
    se registra automáticamente una Infraction con la foto adjunta.
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
        road = Road.objects.select_related('traffic_light').get(id=road_id)
    except Road.DoesNotExist:
        logger.warning("road_id=%d no existe.", road_id)
        return Response(
            {'error': f'road_id={road_id} no existe.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    vehicle_count = int(request.data.get('vehicle_count', 0))
    confidence    = float(request.data.get('confidence', 0.0))
    photo_b64     = request.data.get('photo')

    # Capturar estado del semáforo ANTES de que el signal lo modifique
    try:
        current_light_state = road.traffic_light.state
    except Exception:
        current_light_state = None

    sensor, _ = Sensor.objects.get_or_create(road=road)
    sensor.vehicle_detected = bool(detected)
    sensor.vehicle_count    = max(0, vehicle_count)
    sensor.confidence       = round(max(0.0, min(1.0, confidence)), 3)
    sensor.save()  # dispara control_traffic() via signal

    # Crear infracción si el vehículo cruzó mientras el semáforo estaba en ROJO
    if sensor.vehicle_detected and current_light_state == 'RED':
        try:
            _create_infraction(road, sensor.vehicle_count, sensor.confidence,
                               current_light_state, photo_b64)
        except Exception as exc:
            logger.error("[INFRACCIÓN] Error al crear infracción para via=%s: %s", road.name, exc)

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
