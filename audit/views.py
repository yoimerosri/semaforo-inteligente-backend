from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import AuditLog
from .serializers import AuditLogSerializer
from .helpers import log_audit, get_client_ip

FRONTEND_ALLOWED = {'PAGE_VISIT', 'FRONTEND_ACTION', 'LOGOUT'}


class AuditLogViewSet(viewsets.ModelViewSet):
    queryset           = AuditLog.objects.select_related('usuario').all()
    serializer_class   = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['evento']
    search_fields      = ['usuario_str', 'descripcion', 'ip']
    ordering_fields    = ['timestamp']
    ordering           = ['-timestamp']
    http_method_names  = ['get', 'post', 'head', 'options']

    def create(self, request, *args, **kwargs):
        evento = request.data.get('evento', 'FRONTEND_ACTION')
        if evento not in FRONTEND_ALLOWED:
            evento = 'FRONTEND_ACTION'
        log_audit(
            evento=evento,
            usuario=request.user,
            ip=get_client_ip(request),
            descripcion=request.data.get('descripcion', ''),
            extra=request.data.get('extra', {}),
        )
        return Response({'ok': True}, status=status.HTTP_201_CREATED)
