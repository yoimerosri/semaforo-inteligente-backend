from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.SensorViewSet, basename='sensor')

urlpatterns = [
    # IoT: ESP32 posts sensor readings
    path('update/', views.update_sensor, name='sensor-update'),
    path('', include(router.urls)),
]
