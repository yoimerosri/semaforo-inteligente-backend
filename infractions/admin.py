from django.contrib import admin
from django.utils.html import format_html
from .models import Infraction


@admin.register(Infraction)
class InfractionAdmin(admin.ModelAdmin):
    list_display  = ['road', 'timestamp', 'traffic_light_state', 'vehicle_count',
                     'confidence_display', 'status', 'photo_thumb']
    list_filter   = ['road', 'status', 'traffic_light_state']
    search_fields = ['road__name', 'notes']
    ordering      = ['-timestamp']
    readonly_fields = ['road', 'timestamp', 'traffic_light_state',
                       'vehicle_count', 'confidence', 'photo_thumb']

    @admin.display(description='Confianza')
    def confidence_display(self, obj):
        return f"{obj.confidence:.0%}"

    @admin.display(description='Foto')
    def photo_thumb(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height:80px;border-radius:4px;">',
                obj.photo.url,
            )
        return '—'
