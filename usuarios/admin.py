from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario, Rol, Recurso, UsuarioRol, RolRecurso


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'estado', 'is_staff')
    list_filter = ('estado', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra', {'fields': ('telefono', 'estado')}),
    )


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'estado')
    list_filter = ('estado',)
    search_fields = ('nombre',)


@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'path', 'icono', 'orden', 'recurso_padre', 'estado')
    list_filter = ('estado', 'recurso_padre')
    search_fields = ('nombre', 'path')


@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol')
    list_filter = ('rol',)
    search_fields = ('usuario__username', 'rol__nombre')


@admin.register(RolRecurso)
class RolRecursoAdmin(admin.ModelAdmin):
    list_display = ('rol', 'recurso')
    list_filter = ('rol',)
    search_fields = ('rol__nombre', 'recurso__nombre')
