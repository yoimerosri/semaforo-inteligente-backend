from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    EVENTO_CHOICES = [
        ('LOGIN',                    'Inicio de sesión'),
        ('LOGIN_FAILED',             'Intento de login fallido'),
        ('LOGOUT',                   'Cierre de sesión'),
        ('USER_CREATED',             'Usuario creado'),
        ('USER_UPDATED',             'Usuario actualizado'),
        ('PASSWORD_RESET_REQUESTED', 'Solicitud de restablecimiento de contraseña'),
        ('PASSWORD_RESET_DONE',      'Contraseña restablecida'),
        ('ROLE_ASSIGNED',            'Rol asignado'),
        ('LIGHT_OVERRIDE',           'Control manual de semáforo'),
        ('LIGHT_AUTO',               'Semáforo liberado a automático'),
        ('PAGE_VISIT',               'Visita de módulo'),
        ('FRONTEND_ACTION',          'Acción en el sistema'),
    ]

    evento      = models.CharField(max_length=40, choices=EVENTO_CHOICES, db_index=True)
    usuario     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
    )
    usuario_str = models.CharField(max_length=150, blank=True)
    ip          = models.GenericIPAddressField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True, db_index=True)
    extra       = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Registro de auditoría'
        verbose_name_plural = 'Registros de auditoría'

    def __str__(self):
        ts = self.timestamp.strftime('%Y-%m-%d %H:%M') if self.timestamp else '?'
        return f'[{ts}] {self.evento} — {self.usuario_str or "?"}'
