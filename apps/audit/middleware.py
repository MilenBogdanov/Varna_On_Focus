from .context import set_current_user


class CurrentUserAuditMiddleware:
    """
    Запазва текущия user в thread-local контекст за audit записи.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else None
        set_current_user(user)

        try:
            response = self.get_response(request)
        finally:
            set_current_user(None)

        return response