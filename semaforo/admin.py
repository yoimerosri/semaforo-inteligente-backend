from django.contrib import admin
from .models import Intersection, Road, TrafficLight


@admin.register(Intersection)
class IntersectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Road)
class RoadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_main', 'intersection')
    list_filter = ('is_main', 'intersection')
    search_fields = ('name',)


@admin.register(TrafficLight)
class TrafficLightAdmin(admin.ModelAdmin):
    list_display = ('road', 'state', 'manual_override', 'updated_at')
    list_filter = ('state', 'manual_override')
    readonly_fields = ('updated_at',)
