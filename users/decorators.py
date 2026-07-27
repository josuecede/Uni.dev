from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def admin_required(view_func=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_admin(),
        login_url='login',
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def manager_required(view_func=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and (u.is_admin() or u.is_manager()),
        login_url='login',
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
