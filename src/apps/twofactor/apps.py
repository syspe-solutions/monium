from django.apps import AppConfig


class TwofactorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.twofactor"
    verbose_name = "Autenticação em duas etapas"
