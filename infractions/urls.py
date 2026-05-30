from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import InfractionViewSet, report_infraction, update_plate_view

router = DefaultRouter()
router.register(r'', InfractionViewSet, basename='infraction')

urlpatterns = [
    path('report/', report_infraction, name='infraction-report'),
    path('<int:pk>/placa/', update_plate_view, name='infraction-placa'),
] + router.urls
