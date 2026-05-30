from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import InfractionViewSet, report_infraction

router = DefaultRouter()
router.register(r'', InfractionViewSet, basename='infraction')

urlpatterns = [
    path('report/', report_infraction, name='infraction-report'),
] + router.urls
