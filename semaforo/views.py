from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.permissions import IoTApiKeyPermission
from .models import TrafficLight, Road, Intersection
from .serializers import (
    TrafficLightSerializer,
    TrafficLightControlSerializer,
    RoadSerializer,
    IntersectionSerializer,
)


# ==============================================================================
# IoT endpoint — sensor update triggers automatic control (called by ESP32)
# Authenticated via X-Api-Key header, not JWT.
# ==============================================================================

@api_view(['POST'])
@permission_classes([IoTApiKeyPermission])
def sensor_update(request):
    """
    Receives vehicle detection data from the ESP32 and persists it.
    Automatic traffic control is triggered by the post_save signal on Sensor.
    """
    from sensores.models import Sensor

    road_id = request.data.get('road_id')
    detected = request.data.get('vehicle_detected')

    if road_id is None or detected is None:
        return Response({'error': 'road_id y vehicle_detected son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        sensor, created = Sensor.objects.get_or_create(road_id=road_id)
    except Exception:
        return Response({'error': 'road_id inválido.'}, status=status.HTTP_400_BAD_REQUEST)

    sensor.vehicle_detected = bool(detected)
    sensor.save()

    return Response({'status': 'ok', 'road_id': road_id, 'detected': detected})


# ==============================================================================
# IoT endpoint — report current light state (called by ESP32)
# ==============================================================================

@api_view(['POST'])
@permission_classes([IoTApiKeyPermission])
def report_state(request):
    """ESP32 reports the current state it is showing (informational)."""
    road_id = request.data.get('road_id')
    estado = request.data.get('estado')

    if road_id is None or estado is None:
        return Response({'error': 'road_id y estado son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

    estado_map = {'rojo': 'RED', 'amarillo': 'YELLOW', 'verde': 'GREEN'}
    state = estado_map.get(str(estado).lower())

    if not state:
        return Response({'error': 'Estado inválido. Use rojo, amarillo o verde.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        tl = TrafficLight.objects.get(road_id=road_id)
        # Only update if not under manual override so we don't overwrite operator commands.
        if not tl.manual_override:
            tl.state = state
            tl.save(update_fields=['state', 'updated_at'])
    except TrafficLight.DoesNotExist:
        return Response({'error': 'Semáforo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'status': 'ok', 'road_id': road_id, 'state': state})


# ==============================================================================
# IoT endpoint — ESP32 startup: clear stale overrides + sensors, reset to default
# ==============================================================================

@api_view(['POST'])
@permission_classes([IoTApiKeyPermission])
def startup_reset(request):
    """
    Called by ESP32 on every boot.
    Clears manual overrides and stale sensor detections, then runs control_traffic()
    so the backend always reflects the default state (main roads GREEN) on startup.
    """
    from sensores.models import Sensor
    from .services import control_traffic

    TrafficLight.objects.update(manual_override=False)
    Sensor.objects.update(vehicle_detected=False)
    control_traffic()

    lights = TrafficLight.objects.select_related('road').all()
    return Response(TrafficLightSerializer(lights, many=True).data)


# ==============================================================================
# Read lights — used by ESP32 to check for manual overrides
# ==============================================================================

@api_view(['GET'])
@permission_classes([IoTApiKeyPermission | IsAuthenticated])
def get_lights(request):
    lights = TrafficLight.objects.select_related('road').all()
    return Response(TrafficLightSerializer(lights, many=True).data)


# ==============================================================================
# Manual control — frontend operator sets a specific state
# ==============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manual_control(request):
    """
    Frontend sends road_id + estado + manual_override.
    Setting manual_override=False releases the light back to automatic control.
    """
    serializer = TrafficLightControlSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    road_id = serializer.validated_data['road_id']
    estado = serializer.validated_data['estado']
    override = serializer.validated_data['manual_override']

    estado_map = {'rojo': 'RED', 'amarillo': 'YELLOW', 'verde': 'GREEN'}

    try:
        tl = TrafficLight.objects.get(road_id=road_id)
    except TrafficLight.DoesNotExist:
        return Response({'error': 'Semáforo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    tl.state = estado_map[estado]
    tl.manual_override = override
    tl.save(update_fields=['state', 'manual_override', 'updated_at'])

    return Response(TrafficLightSerializer(tl).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def release_override(request, road_id):
    """Release manual override for a specific road, returning it to automatic mode."""
    try:
        tl = TrafficLight.objects.get(road_id=road_id)
    except TrafficLight.DoesNotExist:
        return Response({'error': 'Semáforo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    tl.manual_override = False
    tl.save(update_fields=['manual_override', 'updated_at'])

    from .services import control_traffic
    control_traffic()

    return Response({'status': 'ok', 'road_id': road_id, 'manual_override': False})


# ==============================================================================
# Read-only ViewSets for roads and intersections
# ==============================================================================

class RoadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Road.objects.select_related('intersection').all()
    serializer_class = RoadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class IntersectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Intersection.objects.all()
    serializer_class = IntersectionSerializer
    permission_classes = [IsAuthenticated]
