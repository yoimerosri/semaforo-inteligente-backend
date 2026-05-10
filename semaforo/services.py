"""
Traffic control business logic.

Precedence:
  1. If any TrafficLight has manual_override=True, the automatic logic skips that light.
  2. Secondary roads with a detected vehicle take priority over main roads.
  3. If no secondary sensor is active, main roads (is_main=True) are set GREEN.
"""

from .models import Road, TrafficLight


def control_traffic():
    """
    Evaluate all sensors and set TrafficLight states accordingly.
    Lights with manual_override=True are left untouched.
    """
    from sensores.models import Sensor

    overridden_road_ids = set(
        TrafficLight.objects.filter(manual_override=True).values_list('road_id', flat=True)
    )

    active_secondary = Sensor.objects.filter(
        vehicle_detected=True,
        road__is_main=False,
    ).exclude(road_id__in=overridden_road_ids).select_related('road')

    roads = Road.objects.select_related('traffic_light').all()

    if active_secondary.exists():
        priority_road = active_secondary.first().road
        for road in roads:
            if road.id in overridden_road_ids:
                continue
            tl = road.traffic_light
            tl.state = TrafficLight.State.GREEN if road == priority_road else TrafficLight.State.RED
            tl.save(update_fields=['state', 'updated_at'])
    else:
        for road in roads:
            if road.id in overridden_road_ids:
                continue
            tl = road.traffic_light
            tl.state = TrafficLight.State.GREEN if road.is_main else TrafficLight.State.RED
            tl.save(update_fields=['state', 'updated_at'])
