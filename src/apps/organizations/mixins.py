from django.contrib.auth.mixins import UserPassesTestMixin

from apps.audit.dtos import SecurityAction, SecurityStatus
from apps.audit.loggers.security_logger import SecurityLogger

from .models import Membership, MembershipRole


class _MembershipRoleRequiredMixin(UserPassesTestMixin):
    """Base para mixins que exigem um dos papéis permitidos na organização ativa.
    Subclasses definem `allowed_roles`."""

    raise_exception = True
    security_logger = SecurityLogger()
    allowed_roles: frozenset = frozenset()

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            self._log_unauthorized("Anonymous user attempted to access organization management")
            return False

        organization = getattr(self.request, "organization", None)
        if organization is None:
            self._log_unauthorized("User has no active organization")
            return False

        has_required_role = Membership.objects.filter(
            organization=organization, user=user, role__in=self.allowed_roles
        ).exists()
        if not has_required_role:
            self._log_unauthorized(f"User lacks required role in organization {organization.id}")
        return has_required_role

    def _log_unauthorized(self, reason):
        self.security_logger.log_event(
            user=self.request.user if self.request.user.is_authenticated else "Anonymous",
            ip_address=self.request.META.get("REMOTE_ADDR"),
            action=SecurityAction.UNAUTHORIZED_ACCESS,
            status=SecurityStatus.FAILED,
            reason=reason,
        )


class OrganizationOwnerRequiredMixin(_MembershipRoleRequiredMixin):
    allowed_roles = frozenset({MembershipRole.OWNER})


class MemberManagementRequiredMixin(_MembershipRoleRequiredMixin):
    """Permite gestão de membros (criar, remover, trocar papel) a OWNER e ADMIN."""

    allowed_roles = frozenset({MembershipRole.OWNER, MembershipRole.ADMIN})


class InventoryWriteRequiredMixin(_MembershipRoleRequiredMixin):
    """Permite cadastro/importação de itens e imóveis a OWNER, ADMIN, MANAGER e OPERATOR —
    exclui VIEWER, que tem acesso somente leitura."""

    allowed_roles = frozenset({
        MembershipRole.OWNER,
        MembershipRole.ADMIN,
        MembershipRole.MANAGER,
        MembershipRole.OPERATOR,
    })
