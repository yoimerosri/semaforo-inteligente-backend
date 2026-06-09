from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = AuditLog.objects.select_related('usuario').all()
    serializer_class   = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['evento']
    search_fields      = ['usuario_str', 'descripcion', 'ip']
    ordering_fields    = ['timestamp']
    ordering           = ['-timestamp']
