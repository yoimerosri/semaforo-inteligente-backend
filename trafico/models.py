from django.db import models
from semaforo.models import Road

class TrafficRecord(models.Model):
    road             = models.ForeignKey(Road, on_delete=models.CASCADE)
    vehicle_detected = models.BooleanField()
    vehicle_count    = models.PositiveSmallIntegerField(default=0)
    confidence       = models.FloatField(default=0.0)
    timestamp        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.road.name} - {self.vehicle_detected} - {self.timestamp}"