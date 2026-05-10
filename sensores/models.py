from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from semaforo.models import Road


class Sensor(models.Model):
    road             = models.OneToOneField(
        Road,
        on_delete=models.CASCADE,
        related_name='sensor',
    )
    vehicle_detected = models.BooleanField(default=False)
    vehicle_count    = models.PositiveSmallIntegerField(default=0)
    confidence       = models.FloatField(default=0.0)

    class Meta:
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensores'

    def __str__(self):
        return f'Sensor — {self.road.name}'


@receiver(post_save, sender=Sensor)
def on_sensor_save(sender, instance, **kwargs):
    from semaforo.services import control_traffic
    control_traffic()

    from trafico.models import TrafficRecord
    TrafficRecord.objects.create(
        road=instance.road,
        vehicle_detected=instance.vehicle_detected,
        vehicle_count=instance.vehicle_count,
        confidence=instance.confidence,
    )
