import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_audit(evento, usuario=None, ip=None, descripcion='', extra=None):
    try:
        from .models import AuditLog  # import local para evitar circular
        AuditLog.objects.create(
            evento=evento,
            usuario=usuario,
            usuario_str=getattr(usuario, 'username', '') or '',
            ip=ip,
            descripcion=descripcion,
            extra=extra or {},
        )
    except Exception as exc:
        logger.error('[AUDIT] log_audit error: %s', exc)
