from django.test.runner import DiscoverRunner

BOOTSTRAP_ADMIN_USERNAME = "test-bootstrap-admin"


class MoniumTestRunner(DiscoverRunner):
    """SetupRequiredMiddleware (apps.setup) bloqueia toda a navegação até existir
    um superusuário — sem isso, qualquer teste que bata numa página comum
    (login, settings, etc.) seria redirecionado pro instalador. Criamos um
    superusuário de baseline uma vez, antes de qualquer teste rodar; apps.setup
    testa o cenário "sem superusuário" limpando essa baseline no próprio setUp."""

    def setup_databases(self, **kwargs):
        result = super().setup_databases(**kwargs)
        self._create_bootstrap_superuser()
        return result

    def _create_bootstrap_superuser(self):
        from django.contrib.auth import get_user_model

        user_model = get_user_model()
        if user_model.objects.filter(username=BOOTSTRAP_ADMIN_USERNAME).exists():
            return
        user_model.objects.create_superuser(
            username=BOOTSTRAP_ADMIN_USERNAME,
            email="test-bootstrap-admin@example.com",
            password="Strong@Password123",
        )
