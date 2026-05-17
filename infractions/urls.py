from rest_framework.routers import DefaultRouter
from .views import InfractionViewSet

router = DefaultRouter()
router.register(r'', InfractionViewSet, basename='infraction')

urlpatterns = router.urls
