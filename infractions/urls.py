from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import InfractionViewSet, report_infraction

router = DefaultRouter()
router.register(r'', InfractionViewSet, basename='infraction')

# URL explícita para edición de placa (garantiza registro independiente del router)
_update_plate = InfractionViewSet.as_view({'patch': 'update_plate'})

urlpatterns = [
    path('report/', report_infraction, name='infraction-report'),
    path('<int:pk>/placa/', _update_plate, name='infraction-placa'),
] + router.urls
