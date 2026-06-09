import logging

from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created

from .helpers import get_client_ip, log_audit

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    try:
        ip = get_client_ip(request) if request else None
        log_audit(
            evento='LOGIN',
            usuario=user,
            ip=ip,
            descripcion=f'Inicio de sesión exitoso: {user.username}',
        )
    except Exception as exc:
        logger.error('[AUDIT] on_login: %s', exc)


@receiver(user_login_failed)
def on_login_failed(sender, credentials, request, **kwargs):
    try:
        ip = get_client_ip(request) if request else None
        username = (credentials or {}).get('username', '?')
        log_audit(
            evento='LOGIN_FAILED',
            ip=ip,
            descripcion=f'Intento de login fallido — usuario: {username}',
            extra={'username': username},
        )
    except Exception as exc:
        logger.error('[AUDIT] on_login_failed: %s', exc)


@receiver(post_save, sender='usuarios.Usuario')
def on_user_saved(sender, instance, created, **kwargs):
    try:
        if created:
            log_audit(
                evento='USER_CREATED',
                usuario=instance,
                descripcion=f'Nuevo usuario creado: {instance.username} ({instance.email})',
            )
        else:
            log_audit(
                evento='USER_UPDATED',
                usuario=instance,
                descripcion=f'Usuario actualizado: {instance.username}',
            )
    except Exception as exc:
        logger.error('[AUDIT] on_user_saved: %s', exc)


@receiver(reset_password_token_created)
def on_password_reset_requested(sender, instance, reset_password_token, **kwargs):
    try:
        user = reset_password_token.user
        log_audit(
            evento='PASSWORD_RESET_REQUESTED',
            usuario=user,
            descripcion=f'Solicitud de restablecimiento de contraseña para: {user.email}',
        )
    except Exception as exc:
        logger.error('[AUDIT] on_password_reset_requested: %s', exc)
