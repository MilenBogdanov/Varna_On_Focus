from django.apps import AppConfig


class SignalsConfig(AppConfig):
    name = 'apps.signals'
    verbose_name = 'Сигнали'

    def ready(self):
        import apps.signals.signals