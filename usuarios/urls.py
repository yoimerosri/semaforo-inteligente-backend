from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from django_rest_passwordreset.views import (
    reset_password_request_token,
    reset_password_confirm,
    reset_password_validate_token,
)

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
    # Password reset — re_path con slash opcional para evitar que un redirect 301
    # convierta el POST en GET (comportamiento del navegador con APPEND_SLASH).
    re_path(r'^password_reset/?$',                    reset_password_request_token, name='password-reset-request'),
    re_path(r'^password_reset/confirm/?$',            reset_password_confirm,       name='password-reset-confirm'),
    re_path(r'^password_reset/validate_token/?$',     reset_password_validate_token, name='password-reset-validate'),
    path('', include(router.urls)),
]
