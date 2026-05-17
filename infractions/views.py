import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Infraction
from .serializers import InfractionSerializer

logger = logging.getLogger(__name__)


class InfractionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lista y detalle de infracciones. Solo lectura desde el ViewSet base.
    La creación ocurre automáticamente desde sensores/views.py.
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

        logger.info(
            "[INFRACCIÓN] id=%d  via=%s  nuevo_estado=%s",
            infraction.id, infraction.road.name, new_status,
        )
        return Response(self.get_serializer(infraction).data)
