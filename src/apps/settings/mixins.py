from django.contrib.auth.mixins import UserPassesTestMixin

from apps.audit.dtos import SecurityAction, SecurityStatus
from apps.audit.loggers.security_logger import SecurityLogger


class StaffRequiredMixin(UserPassesTestMixin):
    """Restringe o acesso às telas de configuração do sistema a usuários staff."""

    raise_exception = True
    security_logger = SecurityLogger()

    def test_func(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return True
        self._log_unauthorized(user)
        return False

    def _log_unauthorized(self, user):
        self.security_logger.log_event(
            user=user if user.is_authenticated else "Anonymous",
            ip_address=self.request.META.get("REMOTE_ADDR"),
            action=SecurityAction.UNAUTHORIZED_ACCESS,
            status=SecurityStatus.FAILED,
            reason="User lacks staff permission to access system settings",
        )
