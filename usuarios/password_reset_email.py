import logging
import resend

from django.conf import settings
from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(reset_password_token_created)
def send_password_reset_email(sender, instance, reset_password_token, *args, **kwargs):
    user      = reset_password_token.user
    token     = reset_password_token.key
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    full_name = f"{user.first_name} {user.last_name}".strip()
    name      = full_name or user.username

    html_body = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:40px 0;background:#02040e;font-family:Inter,system-ui,sans-serif;">
  <table align="center" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background:rgba(255,255,255,0.04);border:1px solid rgba(0,212,255,0.18);border-radius:16px;overflow:hidden;">
    <tr>
      <td style="background:linear-gradient(135deg,rgba(0,212,255,0.12) 0%,rgba(0,255,157,0.07) 100%);padding:32px;text-align:center;border-bottom:1px solid rgba(0,212,255,0.18);">
        <div style="display:inline-flex;gap:10px;margin-bottom:14px;">
          <div style="width:18px;height:18px;border-radius:50%;background:#ef4444;box-shadow:0 0 10px #ef4444;"></div>
          <div style="width:18px;height:18px;border-radius:50%;background:#eab308;box-shadow:0 0 10px #eab308;"></div>
          <div style="width:18px;height:18px;border-radius:50%;background:#22c55e;box-shadow:0 0 10px #22c55e;"></div>
        </div>
        <h1 style="margin:0;font-size:22px;font-weight:700;color:#00d4ff;">
          Semáforo<span style="color:#00ff9d;">Inteligente</span>
        </h1>
        <p style="margin:6px 0 0;font-size:13px;color:rgba(255,255,255,0.45);">
          Control y monitoreo IoT · Maicao, La Guajira
        </p>
      </td>
    </tr>
    <tr>
      <td style="padding:36px 40px;color:rgba(255,255,255,0.82);">
        <h2 style="margin:0 0 14px;font-size:18px;color:#fff;">Hola, {name}</h2>
        <p style="margin:0 0 10px;line-height:1.65;color:rgba(255,255,255,0.68);">
          Recibimos una solicitud para <strong style="color:#fff;">restablecer tu contraseña</strong>
          en el Sistema de Semáforo Inteligente.
        </p>
        <p style="margin:0 0 28px;line-height:1.65;color:rgba(255,255,255,0.68);">
          Haz clic en el botón de abajo. El enlace es válido por <strong style="color:#fff;">1 hora</strong>.
        </p>
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td align="center" style="padding-bottom:28px;">
              <a href="{reset_url}"
                 style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#00d4ff,#00ff9d);color:#02040e;font-weight:700;font-size:15px;text-decoration:none;border-radius:8px;letter-spacing:0.3px;">
                Restablecer contraseña
              </a>
            </td>
          </tr>
        </table>
        <p style="margin:0 0 8px;font-size:13px;line-height:1.6;color:rgba(255,255,255,0.45);">
          Si no solicitaste esto, ignora este mensaje. Tu contraseña no cambiará.
        </p>
        <p style="margin:0;font-size:11px;color:rgba(255,255,255,0.28);word-break:break-all;">
          O copia este enlace en tu navegador:<br>{reset_url}
        </p>
      </td>
    </tr>
    <tr>
      <td style="padding:18px 40px;border-top:1px solid rgba(255,255,255,0.07);text-align:center;font-size:11px;color:rgba(255,255,255,0.28);">
        Sistema de Semáforo Inteligente · Maicao, La Guajira<br>
        Correo automático — no respondas a este mensaje.
      </td>
    </tr>
  </table>
</body>
</html>"""

    text_body = (
        f"Hola {name},\n\n"
        f"Recibimos una solicitud para restablecer tu contraseña.\n\n"
        f"Ingresa al siguiente enlace (válido por 1 hora):\n{reset_url}\n\n"
        f"Si no solicitaste esto, ignora este mensaje."
    )

    try:
        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send({
            "from":    settings.DEFAULT_FROM_EMAIL,
            "to":      [user.email],
            "subject": "Recuperación de contraseña — Semáforo Inteligente",
            "html":    html_body,
            "text":    text_body,
        })
        logger.info("[PASSWORD RESET] Email enviado a %s (user=%s)", user.email, user.username)
    except Exception as exc:
        logger.error("[PASSWORD RESET] Error enviando email a %s: %s", user.email, exc)
