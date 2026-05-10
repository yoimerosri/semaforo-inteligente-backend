from django.core.management.base import BaseCommand

from semaforo.models import Intersection, Road, TrafficLight
from sensores.models import Sensor


INTERSECTION_NAME = "Intersección Maicao"

ROADS = [
    {"name": "Maicao",   "is_main": True},
    {"name": "Riohacha", "is_main": True},
    {"name": "Uribia",   "is_main": False},
    {"name": "Albania",  "is_main": False},
]


class Command(BaseCommand):
    help = "Crea la intersección, vías, semáforos y sensores iniciales si no existen."

    def handle(self, *args, **options):
        intersection, created = Intersection.objects.get_or_create(name=INTERSECTION_NAME)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Intersección creada: {INTERSECTION_NAME}"))
        else:
            self.stdout.write(f"Intersección ya existe: {INTERSECTION_NAME}")

        for road_data in ROADS:
            road, created = Road.objects.get_or_create(
                name=road_data["name"],
                defaults={"is_main": road_data["is_main"], "intersection": intersection},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Vía creada: {road.name} (main={road.is_main})"))
            else:
                self.stdout.write(f"  Vía ya existe: {road.name}")

            light, created = TrafficLight.objects.get_or_create(
                road=road,
                defaults={"state": TrafficLight.State.RED},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"    Semáforo creado para: {road.name}"))

            sensor, created = Sensor.objects.get_or_create(
                road=road,
                defaults={"vehicle_detected": False},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"    Sensor creado para: {road.name}"))

        self.stdout.write(self.style.SUCCESS("\nSeed completado correctamente."))
