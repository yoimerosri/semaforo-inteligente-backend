from django.conf import settings
from rest_framework.permissions import BasePermission


class IsAdminOrStaff(BasePermission):
    """Only Django staff / superuser can access."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class HasResourcePermission(BasePermission):
    """
    Checks that the authenticated user has a Recurso whose url_backend
    matches the current request path.  Superusers bypass this check.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        path = request.path
        return request.user.recursos_list.filter(url_backend=path).exists()


class IoTApiKeyPermission(BasePermission):
    """
    Validates the X-Api-Key header against the IOT_API_KEY setting.
    Used for ESP32 endpoints that cannot perform an OAuth flow.
    """

    def has_permission(self, request, view):
        api_key = request.headers.get('X-Api-Key', '')
        return api_key == settings.IOT_API_KEY
