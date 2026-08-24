from django.contrib.auth.mixins import UserPassesTestMixin

from apps.audit.dtos import SecurityAction, SecurityStatus
from apps.audit.loggers.security_logger import SecurityLogger
from apps.organizations.models import Membership, MembershipRole


class PermissionRequiredMixin(UserPassesTestMixin):
    """Restringe o acesso a quem é OWNER de pelo menos uma organização —
    hoje usado só pelos dashboards de auditoria/log, que são visão de
    administração do sistema, não de uma organização específica."""

    security_logger = SecurityLogger()

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            self._log_unauthorized("Anonymous user attempted to access protected view")
            return False

        is_owner = Membership.objects.filter(user=user, role=MembershipRole.OWNER).exists()
        if not is_owner:
            self._log_unauthorized("User is not an organization owner")

        return is_owner

    def _log_unauthorized(self, reason):
        self.security_logger.log_event(
            user=self.request.user if self.request.user.is_authenticated else "Anonymous",
            ip_address=self.request.META.get('REMOTE_ADDR'),
            action=SecurityAction.UNAUTHORIZED_ACCESS,
            status=SecurityStatus.FAILED,
            reason=reason,
        )

class UserRoleMixin:
    def get_user_role(self):
        user = self.request.user
        if hasattr(user, "employee_profile"):
            return user.employee_profile
        return None
