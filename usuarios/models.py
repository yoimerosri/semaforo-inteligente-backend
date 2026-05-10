from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True, null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    @property
    def roles_list(self):
        return list(self.usuario_roles.select_related('rol').values_list('rol__nombre', flat=True))

    @property
    def recursos_list(self):
        role_ids = self.usuario_roles.values_list('rol_id', flat=True)
        return Recurso.objects.filter(
            rol_recursos__rol_id__in=role_ids
        ).distinct().order_by('orden')


class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Recurso(models.Model):
    nombre = models.CharField(max_length=100)
    url_backend = models.CharField(max_length=255, blank=True)
    url_frontend = models.CharField(max_length=255, blank=True)
    path = models.CharField(max_length=255, blank=True)
    icono = models.CharField(max_length=100, blank=True)
    orden = models.PositiveSmallIntegerField(default=0)
    recurso_padre = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='hijos',
    )
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class UsuarioRol(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='usuario_roles',
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        related_name='usuario_roles',
    )

    class Meta:
        unique_together = ('usuario', 'rol')
        verbose_name = 'Usuario-Rol'
        verbose_name_plural = 'Usuarios-Roles'

    def __str__(self):
        return f'{self.usuario} -> {self.rol}'


class RolRecurso(models.Model):
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        related_name='rol_recursos',
    )
    recurso = models.ForeignKey(
        Recurso,
        on_delete=models.CASCADE,
        related_name='rol_recursos',
    )

    class Meta:
        unique_together = ('rol', 'recurso')
        verbose_name = 'Rol-Recurso'
        verbose_name_plural = 'Roles-Recursos'

    def __str__(self):
        return f'{self.rol} -> {self.recurso}'
