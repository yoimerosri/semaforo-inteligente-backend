"""Script para crear datos de prueba: Intersection, Road y TrafficLight."""
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from semaforo.models import Intersection, Road, TrafficLight

inter, _ = Intersection.objects.get_or_create(name="Interseccion Norte")
road, created = Road.objects.get_or_create(
    id=1,
    defaults={"name": "Via principal Norte", "is_main": True, "intersection": inter},
)
tl, _ = TrafficLight.objects.get_or_create(
    road=road,
    defaults={"state": TrafficLight.State.RED},
)
print(f"Road id={road.id}  name={road.name}  is_main={road.is_main}  created={created}")
print(f"TrafficLight state={tl.state}  override={tl.manual_override}")
