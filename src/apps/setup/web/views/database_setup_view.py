from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import View

from apps.setup.services.database_connection_tester_service import (
    DatabaseConnectionTestError,
    DatabaseConnectionTesterService,
)
from apps.setup.services.runtime_database_config_service import RuntimeDatabaseConfigService
from apps.setup.services.server_restart_service import ServerRestartService

from ..forms import DatabaseSetupForm


class DatabaseSetupView(View):
    template_name = "setup/database.html"
    restarting_template_name = "setup/restarting.html"
    current_step = 1

    def get(self, request):
        self._guard_setup_still_pending()
        form = DatabaseSetupForm(initial=self._prefill(request))
        return render(request, self.template_name, self._context(form))

    def post(self, request):
        self._guard_setup_still_pending()

        form = DatabaseSetupForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, self._context(form))

        configuration = form.to_configuration()

        try:
            DatabaseConnectionTesterService().test(configuration)
        except DatabaseConnectionTestError as error:
            form.add_error(None, str(error))
            return render(request, self.template_name, self._context(form))

        return self._activate(request, configuration)

    def _activate(self, request, configuration):
        runtime_config_service = RuntimeDatabaseConfigService()
        runtime_config_service.persist(configuration)

        if configuration.engine == "sqlite3":
            # Já era o banco em uso (default antes do instalador confirmar) —
            # não precisa reiniciar o processo, só liberar o próximo passo.
            runtime_config_service.apply_without_restart()
            return redirect("setup:admin")

        ServerRestartService().schedule_restart()
        return render(request, self.restarting_template_name, {"current_step": self.current_step})

    def _context(self, form):
        return {"form": form, "current_step": self.current_step}

    def _prefill(self, request):
        """Pré-preenche host/porta/nome/usuário com a última escolha salva —
        relevante ao voltar do passo do administrador pra revisar o banco.
        A senha nunca é reexibida; se deixada em branco, precisa ser digitada
        de novo."""
        persisted = RuntimeDatabaseConfigService().load_persisted()
        if not persisted:
            return None
        return {
            "engine": persisted.engine,
            "host": persisted.host,
            "port": persisted.port,
            "name": persisted.name,
            "user": persisted.user,
        }

    def _guard_setup_still_pending(self):
        # Enquanto a instalação não estiver 100% concluída (banco configurado
        # E um superusuário já criado), os dois passos ficam livremente
        # navegáveis entre si — permite voltar pra revisar a escolha de banco.
        if not settings.DATABASE_SETUP_REQUIRED and get_user_model().objects.filter(is_superuser=True).exists():
            raise Http404()
