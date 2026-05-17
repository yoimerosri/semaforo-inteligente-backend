import base64
import logging
import time

from django.core.files.base import ContentFile
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.permissions import IoTApiKeyPermission
from semaforo.models import Road
from .models import Infraction
from .serializers import InfractionSerializer

logger = logging.getLogger(__name__)


class InfractionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lista y detalle de infracciones (lectura para el frontend).
    La creación ocurre desde el endpoint report/ (visión con tracking).
    La revisión (verificar / desestimar) se hace con el action update_status.
    """
    queryset           = Infraction.objects.select_related('road').all()
    serializer_class   = InfractionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['road', 'status', 'traffic_light_state']
    search_fields      = ['road__name', 'notes']
    ordering_fields    = ['timestamp', 'confidence', 'vehicle_count']
    ordering           = ['-timestamp']

    @action(detail=True, methods=['patch'], url_path='estado')
    def update_status(self, request, pk=None):
        """
        PATCH /api/infractions/<id>/estado/
        Payload: { "status": "VERIFIED" | "DISMISSED", "notes": "..." }
        """
        infraction = self.get_object()

        new_status = request.data.get('status')
        if new_status not in (Infraction.Status.VERIFIED, Infraction.Status.DISMISSED):
            return Response(
                {'error': 'Estado inválido. Use VERIFIED o DISMISSED.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        infraction.status = new_status
        if 'notes' in request.data:
            infraction.notes = request.data['notes']
        infraction.save(update_fields=['status', 'notes'])

        logger.info("[INFRACCIÓN] id=%d  via=%s  nuevo_estado=%s",
                    infraction.id, infraction.road.name, new_status)
        return Response(self.get_serializer(infraction).data)


@api_view(['POST'])
@permission_classes([IoTApiKeyPermission])
def report_infraction(request):
    """
    POST /api/infractions/report/

    Llamado por el módulo de visión cuando un vehículo cruza la línea virtual.
    El backend verifica si el semáforo de esa vía está en ROJO:
      - ROJO  → crea la Infraction con foto y devuelve created=True
      - Otro  → ignora y devuelve created=False

    Payload:
        road_id  (int,  requerido)
        photo    (str,  opcional — base64 JPEG)
    """
    road_id = request.data.get('road_id')
    if road_id is None:
        return Response({'error': 'road_id es requerido.'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        road_id = int(road_id)
    except (TypeError, ValueError):
        return Response({'error': 'road_id debe ser un entero.'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        road = Road.objects.select_related('traffic_light').get(id=road_id)
    except Road.DoesNotExist:
        return Response({'error': f'road_id={road_id} no existe.'},
                        status=status.HTTP_404_NOT_FOUND)

    # Verificar estado actual del semáforo
    try:
        light_state = road.traffic_light.state
    except Exception:
        return Response({'created': False, 'reason': 'semáforo no configurado'})

    if light_state != 'RED':
        logger.debug("[INFRACCIÓN] ignorada — via=%s  state=%s  (no es ROJO)",
                     road.name, light_state)
        return Response({'created': False, 'reason': f'semáforo en {light_state}'})

    # Crear infracción
    intr = Infraction(
        road=road,
        traffic_light_state=light_state,
        vehicle_count=1,
        confidence=1.0,
    )

    photo_b64 = request.data.get('photo')
    if photo_b64:
        try:
            img_bytes = base64.b64decode(photo_b64)
            filename  = f"inf_{road_id}_{int(time.time())}.jpg"
            intr.photo.save(filename, ContentFile(img_bytes), save=False)
        except Exception as exc:
            logger.warning("[INFRACCIÓN] No se pudo guardar la foto: %s", exc)

    intr.save()

    logger.warning("[INFRACCIÓN] CREADA — id=%d  via=%-20s  foto=%s",
                   intr.id, road.name, "sí" if intr.photo else "no")

    return Response({'created': True, 'id': intr.id}, status=status.HTTP_201_CREATED)
