from django.db import models
from semaforo.models import Intersection


class Dispositivo(models.Model):
    class TipoChoices(models.TextChoices):
        ESP32 = 'ESP32', 'ESP32'
        SENSOR = 'SENSOR', 'Sensor'
        DISPLAY = 'DISPLAY', 'Display'
        OTRO = 'OTRO', 'Otro'

    class EstadoChoices(models.TextChoices):
        ONLINE = 'ONLINE', 'En línea'
        OFFLINE = 'OFFLINE', 'Fuera de línea'
        ERROR = 'ERROR', 'Error'

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TipoChoices.choices, default=TipoChoices.ESP32)
    device_id = models.CharField(max_length=100, unique=True, blank=True)
    firmware_version = models.CharField(max_length=30, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    mac_address = models.CharField(max_length=17, blank=True)
    intersection = models.ForeignKey(
        Intersection,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='dispositivos',
    )
    estado = models.CharField(
        max_length=10,
        choices=EstadoChoices.choices,
        default=EstadoChoices.OFFLINE,
    )
    activo = models.BooleanField(default=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dispositivo'
        verbose_name_plural = 'Dispositivos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.tipo})'
