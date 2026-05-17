from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        # Auth + RBAC
        path('', include('usuarios.urls')),

        # Traffic lights (manual control, state reads)
        path('semaforo/', include('semaforo.urls')),

        # Sensor readings from ESP32
        # /api/sensor/update/ — IoT write
        # /api/sensor/        — DRF read-only list
        path('sensor/', include('sensores.urls')),

        # Traffic history log
        path('trafico/', include('trafico.urls')),

        # IoT device registry
        path('dispositivos/', include('dispositivos.urls')),

        # Photo-infractions (vehicles crossing on red)
        path('infractions/', include('infractions.urls')),
    ])),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
