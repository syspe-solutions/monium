from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

from apps.audit.dtos import SecurityAction, SecurityStatus
from apps.audit.loggers.security_logger import SecurityLogger

from .models import Membership, MembershipRole


class OrganizationOwnerRequiredMixin(UserPassesTestMixin):
    raise_exception = True
    security_logger = SecurityLogger()

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            self._log_unauthorized("Anonymous user attempted to access organization management")
            return False

        organization = getattr(self.request, "organization", None)
        if organization is None:
            self._log_unauthorized("User has no active organization")
            return False

        is_owner = Membership.objects.filter(
            organization=organization, user=user, role=MembershipRole.OWNER
        ).exists()
        if not is_owner:
            self._log_unauthorized(f"User is not OWNER of organization {organization.id}")
        return is_owner

    def _log_unauthorized(self, reason):
        self.security_logger.log_event(
            user=self.request.user if self.request.user.is_authenticated else "Anonymous",
            ip_address=self.request.META.get("REMOTE_ADDR"),
            action=SecurityAction.UNAUTHORIZED_ACCESS,
            status=SecurityStatus.FAILED,
            reason=reason,
        )


class OrganizationNotLockedRequiredMixin(UserPassesTestMixin):
    """Bloqueia escrita (itens, convites, etc.) em organizações que excedem o
    org_limit do plano atual do dono — diferente de OrganizationOwnerRequiredMixin,
    isso não é "sem permissão" (403), é "resolva o excesso do seu plano primeiro"."""

    def test_func(self):
        organization = getattr(self.request, "organization", None)
        if organization is None:
            return True

        from apps.billing import services as billing_services

        return not billing_services.is_organization_locked(organization)

    def handle_no_permission(self):
        messages.error(
            self.request,
            "Esta organização está bloqueada por exceder o limite de organizações do seu "
            "plano atual. Apague uma organização mais recente ou faça upgrade para continuar.",
        )
        return redirect("organizations:members")
