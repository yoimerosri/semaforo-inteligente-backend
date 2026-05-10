"""
Configura las 4 vías del sistema Maicao-Riohacha / Uribia-Albania.

Ejecución:
    cd backend
    python seed_vias.py
"""
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from semaforo.models import Intersection, Road, TrafficLight
from sensores.models import Sensor

# ── Limpiar datos de prueba anteriores ────────────────────────────────────────
Road.objects.all().delete()          # cascade elimina TrafficLight y Sensor
Intersection.objects.all().delete()
print("Datos anteriores eliminados.")

# ── Intersección principal ────────────────────────────────────────────────────
inter = Intersection.objects.create(name="Interseccion Maicao-Uribia")

# ── Vías principales (siempre en VERDE si no hay vehículo en secundarias) ────
maicao = Road.objects.create(
    name="Maicao", is_main=True, intersection=inter
)
riohacha = Road.objects.create(
    name="Riohacha", is_main=True, intersection=inter
)

# ── Vías secundarias (cuando detectan vehículo, las principales van a ROJO) ──
uribia = Road.objects.create(
    name="Uribia", is_main=False, intersection=inter
)
albania = Road.objects.create(
    name="Albania", is_main=False, intersection=inter
)

# ── Semáforos (estado inicial: principales VERDE, secundarias ROJO) ───────────
TrafficLight.objects.create(road=maicao,   state=TrafficLight.State.GREEN)
TrafficLight.objects.create(road=riohacha, state=TrafficLight.State.GREEN)
TrafficLight.objects.create(road=uribia,   state=TrafficLight.State.RED)
TrafficLight.objects.create(road=albania,  state=TrafficLight.State.RED)

# ── Sensores (estado inicial sin vehículo) ────────────────────────────────────
Sensor.objects.create(road=maicao,   vehicle_detected=False)
Sensor.objects.create(road=riohacha, vehicle_detected=False)
Sensor.objects.create(road=uribia,   vehicle_detected=False)
Sensor.objects.create(road=albania,  vehicle_detected=False)

# ── Resumen ───────────────────────────────────────────────────────────────────
print()
print(f"{'VÍA':<12} {'ID':>4}  {'TIPO':<12}  {'SEMÁFORO'}")
print("-" * 45)
for road in Road.objects.select_related('traffic_light').order_by('id'):
    tipo = "PRINCIPAL" if road.is_main else "SECUNDARIA"
    print(f"{road.name:<12} {road.id:>4}  {tipo:<12}  {road.traffic_light.state}")

print()
print("Configura vision/config.py con:")
for road in Road.objects.filter(is_main=False).order_by('id'):
    print(f'  road_id={road.id}  →  "{road.name}"  (cámara secundaria)')
