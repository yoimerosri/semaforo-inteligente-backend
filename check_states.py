import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from semaforo.models import Road
print(f"  {'VIA':<12} {'TIPO':<12} {'SEMAFORO':<8} OVERRIDE")
print(f"  {'-'*46}")
for r in Road.objects.select_related('traffic_light').order_by('id'):
    tipo = "PRINCIPAL" if r.is_main else "SECUNDARIA"
    tl = r.traffic_light
    print(f"  {r.name:<12} {tipo:<12} {tl.state:<8} {tl.manual_override}")
