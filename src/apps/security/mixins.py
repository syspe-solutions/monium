from django.contrib.auth.mixins import UserPassesTestMixin

from apps.audit.dtos import SecurityAction, SecurityStatus
from apps.audit.loggers.security_logger import SecurityLogger


class PermissionRequiredMixin(UserPassesTestMixin):
    required_permission = None
    security_logger = SecurityLogger()

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            self._log_unauthorized("Anonymous user attempted to access protected view")
            return False

        has_permission = (
            self.required_permission 
            and hasattr(user, 'all_permissions') 
            and self.required_permission in user.all_permissions
        )

        if not has_permission:
            self._log_unauthorized(f"User lacks permission: {self.required_permission}")
            
        return has_permission

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
