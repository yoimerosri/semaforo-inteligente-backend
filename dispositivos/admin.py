from django.contrib import admin
from .models import Dispositivo


@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'device_id', 'estado', 'ip_address', 'ultimo_acceso', 'activo')
    list_filter = ('tipo', 'estado', 'activo')
    search_fields = ('nombre', 'device_id', 'mac_address')
    readonly_fields = ('created_at', 'updated_at', 'ultimo_acceso')
