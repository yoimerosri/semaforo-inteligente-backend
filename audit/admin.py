from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display    = ['timestamp', 'evento', 'usuario_str', 'ip', 'descripcion']
    list_filter     = ['evento']
    search_fields   = ['usuario_str', 'ip', 'descripcion']
    readonly_fields = ['evento', 'usuario', 'usuario_str', 'ip', 'descripcion', 'timestamp', 'extra']
    ordering        = ['-timestamp']
