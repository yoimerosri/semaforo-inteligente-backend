from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from infractions.views import update_plate_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        # Auth + RBAC
        path('', include('usuarios.urls')),

        # Traffic lights (manual control, state reads)
        path('semaforo/', include('semaforo.urls')),

        # Sensor readings from ESP32
        path('sensor/', include('sensores.urls')),

        # Traffic history log
        path('trafico/', include('trafico.urls')),

        # IoT device registry
        path('dispositivos/', include('dispositivos.urls')),

        # Plate update — registered here to avoid DRF router conflicts
        path('infractions/set-plate/<int:pk>/', update_plate_view, name='infraction-set-plate'),

        # Photo-infractions (vehicles crossing on red)
        path('infractions/', include('infractions.urls')),
    ])),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
