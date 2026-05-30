import logging

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.permissions import IoTApiKeyPermission, IsAuthenticatedOrIoTKey
from semaforo.models import Road
from .models import Infraction
from .serializers import InfractionSerializer

logger = logging.getLogger(__name__)


class InfractionViewSet(viewsets.ModelViewSet):
    """
    Lista, detalle, edición de placa y eliminación de infracciones.
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

    # Bloquea create/update genéricos — la creación solo va por report/
    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        logger.info("[INFRACCIÓN] ELIMINADA — id=%d  via=%s", instance.id, instance.road.name)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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


@api_view(['PATCH'])
@permission_classes([IsAuthenticatedOrIoTKey])
def update_plate_view(request, pk):
    """
    PATCH /api/infractions/<pk>/placa/
    Acepta API Key IoT (módulo visión) o JWT (frontend).
    Payload: { "plate_number": "ABC123" }  — vacío limpia la placa.
    """
    try:
        infraction = Infraction.objects.get(pk=pk)
    except Infraction.DoesNotExist:
        return Response({'error': 'No encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    plate = (request.data.get('plate_number') or '').strip().upper() or None
    infraction.plate_number = plate
    infraction.save(update_fields=['plate_number'])
    logger.info("[INFRACCIÓN] id=%d  placa actualizada → %s", infraction.id, plate or '—')
    return Response(InfractionSerializer(infraction).data)


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
    try:
        confidence = float(request.data.get('confidence') or 1.0)
    except (TypeError, ValueError):
        confidence = 1.0
    try:
        vehicle_count = int(request.data.get('vehicle_count') or 1)
    except (TypeError, ValueError):
        vehicle_count = 1

    intr = Infraction(
        road=road,
        traffic_light_state=light_state,
        vehicle_count=vehicle_count,
        confidence=confidence,
        photo_b64=request.data.get('photo') or '',
        plate_number=(request.data.get('plate_number') or '').strip().upper() or None,
    )
    intr.save()

    logger.warning("[INFRACCIÓN] CREADA — id=%d  via=%-20s  placa=%-8s  foto=%s",
                   intr.id, road.name,
                   intr.plate_number or '—',
                   "sí" if intr.photo_b64 else "no")

    return Response({
        'created': True,
        'id': intr.id,
        'plate': intr.plate_number,
    }, status=status.HTTP_201_CREATED)
