from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

from .permissions import (
    is_citizen,
    is_municipal_admin,
    is_super_admin,
    is_admin_or_superadmin,
)


def citizen_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not is_citizen(request.user):
            return HttpResponseForbidden("Нямате права за този ресурс.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def municipal_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not is_municipal_admin(request.user):
            return HttpResponseForbidden("Само общински администратор има достъп.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_or_superadmin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not is_admin_or_superadmin(request.user):
            return HttpResponseForbidden("Нямате административни права.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def superadmin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not is_super_admin(request.user):
            return HttpResponseForbidden("Само супер администратор има достъп.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
