from django.shortcuts import redirect
from django.urls import Resolver404, resolve

ACTIVE_ORG_SESSION_KEY = "active_organization_id"

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
    """Resolve a organização ativa da sessão em request.organization e redireciona
    usuários autenticados sem nenhuma organização para o onboarding obrigatório."""

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = self._resolve_active_organization(request)

        if self._requires_organization(request):
            return redirect("organizations:create")
        return self.get_response(request)

    def _resolve_active_organization(self, request):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None

        memberships = list(user.memberships.select_related("organization").order_by("created_at"))
        if not memberships:
            return None

        by_org_id = {str(m.organization_id): m for m in memberships}
        active_id = request.session.get(ACTIVE_ORG_SESSION_KEY)
        membership = by_org_id.get(active_id) if active_id else None

        if membership is None:
            membership = memberships[0]
            request.session[ACTIVE_ORG_SESSION_KEY] = str(membership.organization_id)

        return membership.organization

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

        return request.organization is None
