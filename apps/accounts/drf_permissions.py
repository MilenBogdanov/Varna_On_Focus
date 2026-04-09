from rest_framework.permissions import BasePermission, SAFE_METHODS

from .permissions import (
    is_citizen,
    is_municipal_admin,
    is_super_admin,
    is_admin_or_superadmin,
)


class IsAuthenticatedCitizen(BasePermission):
    """
    Само регистриран гражданин
    """
    def has_permission(self, request, view):
        return is_citizen(request.user)


class IsMunicipalAdmin(BasePermission):
    """
    Само общински администратор
    """
    def has_permission(self, request, view):
        return is_municipal_admin(request.user)


class IsSuperAdmin(BasePermission):
    """
    Само супер администратор
    """
    def has_permission(self, request, view):
        return is_super_admin(request.user)


class IsAdminOrSuperAdmin(BasePermission):
    """
    Общинар или супер админ
    """
    def has_permission(self, request, view):
        return is_admin_or_superadmin(request.user)


class ReadOnlyForGuests(BasePermission):
    """
    Гостите могат само GET (read-only)
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated