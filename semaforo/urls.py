from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('roads', views.RoadViewSet, basename='road')
router.register('intersections', views.IntersectionViewSet, basename='intersection')

urlpatterns = [
    # Read all lights (ESP32 + frontend)
    path('lights/', views.get_lights, name='semaforo-lights'),

    # Manual override from frontend (JWT required)
    path('control/', views.manual_control, name='semaforo-manual-control'),
    path('control/<int:road_id>/release/', views.release_override, name='semaforo-release-override'),

    # IoT: ESP32 reports current state (API key required)
    path('estado/', views.report_state, name='semaforo-report-state'),

    path('', include(router.urls)),
]
