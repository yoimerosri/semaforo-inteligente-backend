from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import TrafficRecord
from .serializers import TrafficRecordSerializer


class TrafficRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrafficRecord.objects.select_related('road').order_by('-timestamp')
    serializer_class = TrafficRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['road', 'vehicle_detected']
    search_fields = ['road__name']
