from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

router = DefaultRouter()
router.register('usuarios', views.UsuarioViewSet, basename='usuario')
router.register('roles', views.RolViewSet, basename='rol')
router.register('recursos', views.RecursoViewSet, basename='recurso')
router.register('usuarios-roles', views.UsuarioRolViewSet, basename='usuario-rol')
router.register('roles-recursos', views.RolRecursoViewSet, basename='rol-recurso')

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('', include(router.urls)),
]
