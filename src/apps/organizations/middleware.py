from django.shortcuts import redirect
from django.urls import Resolver404, resolve

EXEMPT_URL_NAMES = {
    "organizations:create",
    "account:login",
    "account:logout",
    "account:register",
    "account:recovery",
    "account:password_reset_done",
    "account:recovery_confirm",
    "account:password_reset_complete",
}
EXEMPT_PATH_PREFIXES = ("/admin/", "/static/", "/media/", "/i18n/")


class RequireOrganizationMiddleware:
    """Redireciona usuários autenticados sem organização para o onboarding obrigatório."""

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        if self._requires_organization(request):
            return redirect("organizations:create")
        return self.get_response(request)

    def _requires_organization(self, request) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated or user.is_superuser:
            return False

        if request.path.startswith(EXEMPT_PATH_PREFIXES):
            return False

        try:
            match = resolve(request.path)
        except Resolver404:
            return False

        url_name = f"{match.namespace}:{match.url_name}" if match.namespace else match.url_name
        if url_name in EXEMPT_URL_NAMES:
            return False

        return user.organization is None
