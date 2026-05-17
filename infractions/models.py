from django.db import models
from semaforo.models import Road


class Infraction(models.Model):
    class Status(models.TextChoices):
        PENDING   = 'PENDING',   'Pendiente'
        VERIFIED  = 'VERIFIED',  'Verificada'
        DISMISSED = 'DISMISSED', 'Desestimada'

    road                = models.ForeignKey(Road, on_delete=models.CASCADE, related_name='infractions')
    timestamp           = models.DateTimeField(auto_now_add=True)
    traffic_light_state = models.CharField(max_length=10)
    vehicle_count       = models.PositiveSmallIntegerField(default=1)
    confidence          = models.FloatField(default=0.0)
    photo               = models.ImageField(upload_to='infractions/%Y/%m/%d/', blank=True, null=True)
    status              = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    notes               = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Infracción'
        verbose_name_plural = 'Infracciones'
        ordering            = ['-timestamp']

    def __str__(self):
        return f"{self.road.name} — {self.timestamp:%Y-%m-%d %H:%M} — {self.status}"
