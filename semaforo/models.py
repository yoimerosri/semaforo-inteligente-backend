from django.db import models


class Intersection(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Intersección'
        verbose_name_plural = 'Intersecciones'

    def __str__(self):
        return self.name


class Road(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_main = models.BooleanField(default=False)
    intersection = models.ForeignKey(
        Intersection,
        on_delete=models.CASCADE,
        related_name='roads',
    )

    class Meta:
        verbose_name = 'Vía'
        verbose_name_plural = 'Vías'
        ordering = ['-is_main', 'name']

    def __str__(self):
        return self.name


class TrafficLight(models.Model):
    class State(models.TextChoices):
        RED = 'RED', 'Rojo'
        YELLOW = 'YELLOW', 'Amarillo'
        GREEN = 'GREEN', 'Verde'

    road = models.OneToOneField(
        Road,
        on_delete=models.CASCADE,
        related_name='traffic_light',
    )
    state = models.CharField(
        max_length=10,
        choices=State.choices,
        default=State.RED,
    )
    # When True the frontend/operator has set this state manually;
    # the ESP32 respects it instead of following sensor logic.
    manual_override = models.BooleanField(default=False)
    green_duration  = models.PositiveSmallIntegerField(default=5)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Semáforo'
        verbose_name_plural = 'Semáforos'

    def __str__(self):
        return f'{self.road.name} — {self.state}'
