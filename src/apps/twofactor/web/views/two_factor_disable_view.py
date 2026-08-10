from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views import View

from apps.audit.dtos import SecurityAction, SecurityStatus
from apps.audit.loggers.security_logger import SecurityLogger
from apps.twofactor.services import TwoFactorDisableService


class TwoFactorDisableView(LoginRequiredMixin, View):
    def post(self, request):
        disabled = TwoFactorDisableService.disable(request.user)

        if disabled:
            messages.success(request, _("Two-factor authentication has been disabled."))
            SecurityLogger.log_event(
                user=request.user,
                ip_address=request.META.get("REMOTE_ADDR"),
                action=SecurityAction.MFA_DISABLED,
                status=SecurityStatus.SUCCESS,
                reason="2FA disabled by user",
            )

        return redirect("account:settings")
