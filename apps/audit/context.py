import threading


_audit_context = threading.local()


def set_current_user(user):
    _audit_context.user = user


def get_current_user():
    return getattr(_audit_context, "user", None)