from django.core.management.base import BaseCommand
from usuarios.models import Recurso, Rol, RolRecurso


class Command(BaseCommand):
    help = "Agrega el recurso Fotomultas a todos los roles existentes (idempotente)."

    def handle(self, *args, **options):
        rec, created = Recurso.objects.get_or_create(
            url_frontend="/infractions",
            defaults=dict(
                nombre="Fotomultas",
                icono="fa-solid fa-camera",
                orden=4,
                estado=True,
            ),
        )

        if created:
            self.stdout.write(self.style.SUCCESS("Recurso 'Fotomultas' creado."))
        else:
            self.stdout.write("Recurso 'Fotomultas' ya existía — actualizando datos...")
            rec.nombre = "Fotomultas"
            rec.icono  = "fa-solid fa-camera"
            rec.orden  = 4
            rec.estado = True
            rec.save()

        roles = Rol.objects.all()
        nuevos = 0
        for rol in roles:
            _, asignado = RolRecurso.objects.get_or_create(rol=rol, recurso=rec)
            if asignado:
                nuevos += 1
                self.stdout.write(self.style.SUCCESS(f"  Asignado al rol: {rol.nombre}"))

        if nuevos == 0:
            self.stdout.write("El recurso ya estaba asignado a todos los roles.")

        self.stdout.write(self.style.SUCCESS("Listo."))
