from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import Resolver404, resolve

EXEMPT_PATH_PREFIXES = ("/static/", "/media/", "/i18n/")
DATABASE_STEP_URL_NAME = "setup:database"
ADMIN_STEP_URL_NAME = "setup:admin"
SETUP_STEP_URL_NAMES = (DATABASE_STEP_URL_NAME, ADMIN_STEP_URL_NAME)


class SetupRequiredMiddleware:
    """Redireciona toda a navegação pro instalador enquanto o banco não foi
    escolhido/testado (settings.DATABASE_SETUP_REQUIRED) ou enquanto ainda não
    existe nenhum superusuário. Roda antes de sessão/auth: essas tabelas podem
    nem existir ainda na primeira execução.

    Enquanto a instalação não estiver concluída, os dois passos (banco e admin)
    ficam livremente navegáveis entre si — dá pra voltar do passo 2 pro 1 pra
    trocar a escolha de banco antes de criar o administrador."""

    _superuser_exists = False

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        pending_step = self._pending_setup_step(request)
        if pending_step:
            return redirect(pending_step)
        return self.get_response(request)

    def _pending_setup_step(self, request):
        if request.path.startswith(EXEMPT_PATH_PREFIXES):
            return None

        url_name = self._url_name(request.path)

        if settings.DATABASE_SETUP_REQUIRED:
            # Sem banco configurado ainda, nem o passo do admin pode ser pulado
            # pra frente — só o passo do banco é alcançável.
            return None if url_name == DATABASE_STEP_URL_NAME else DATABASE_STEP_URL_NAME

        if self._admin_setup_pending():
            # Banco já configurado, admin ainda não criado: os dois passos
            # ficam navegáveis entre si — dá pra voltar e revisar o banco.
            return None if url_name in SETUP_STEP_URL_NAMES else ADMIN_STEP_URL_NAME

        if url_name in SETUP_STEP_URL_NAMES:
            # Instalação já concluída: essas telas não devem mais estar acessíveis.
            return "account:login"

        return None

    def _admin_setup_pending(self) -> bool:
        if SetupRequiredMiddleware._superuser_exists:
            return False
        exists = get_user_model().objects.filter(is_superuser=True).exists()
        SetupRequiredMiddleware._superuser_exists = exists
        return not exists

    def _url_name(self, path):
        try:
            match = resolve(path)
        except Resolver404:
            return None
        return f"{match.namespace}:{match.url_name}" if match.namespace else match.url_name
