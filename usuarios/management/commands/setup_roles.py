from django.core.management.base import BaseCommand
from usuarios.models import Rol, Recurso, Usuario, UsuarioRol, RolRecurso


class Command(BaseCommand):
    help = "Crea el rol Administrador con todos los recursos y lo asigna al admin."

    def handle(self, *args, **options):
        RolRecurso.objects.all().delete()
        UsuarioRol.objects.all().delete()
        Recurso.objects.all().delete()
        Rol.objects.all().delete()
        self.stdout.write("Datos anteriores eliminados.")

        rol = Rol.objects.create(nombre="Administrador", descripcion="Acceso completo al sistema", estado=True)
        self.stdout.write(self.style.SUCCESS(f"Rol creado: {rol.nombre}"))

        admin_rec = Recurso.objects.create(nombre="Administracion", url_frontend="#", icono="fa-solid fa-gear", orden=4, estado=True)

        recursos_data = [
            dict(nombre="Dashboard",        url_frontend="/dashboard",    icono="fa-solid fa-gauge",         orden=1),
            dict(nombre="Semaforos",         url_frontend="/semaforo",     icono="fa-solid fa-traffic-light", orden=2),
            dict(nombre="Camaras",           url_frontend="/camaras",      icono="fa-solid fa-video",         orden=3),
            dict(nombre="Fotomultas",        url_frontend="/infractions",  icono="fa-solid fa-camera",        orden=4),
            dict(nombre="Usuarios",          url_frontend="/usuarios",     icono="fa-solid fa-users",         orden=1, recurso_padre=admin_rec),
            dict(nombre="Roles y Permisos",  url_frontend="/roles",        icono="fa-solid fa-user-shield",   orden=2, recurso_padre=admin_rec),
            dict(nombre="Dispositivos IoT",  url_frontend="/dispositivos", icono="fa-solid fa-microchip",     orden=3, recurso_padre=admin_rec),
        ]

        todos = [admin_rec]
        for r in recursos_data:
            rec = Recurso.objects.create(estado=True, **r)
            todos.append(rec)
            self.stdout.write(self.style.SUCCESS(f"  Recurso: {rec.nombre}"))

        for rec in todos:
            RolRecurso.objects.create(rol=rol, recurso=rec)

        admin = Usuario.objects.get(username="admin")
        UsuarioRol.objects.create(usuario=admin, rol=rol)
        self.stdout.write(self.style.SUCCESS(f"Rol '{rol.nombre}' asignado a '{admin.username}'."))
        self.stdout.write(self.style.SUCCESS("Configuracion completada."))
