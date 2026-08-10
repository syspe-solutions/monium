from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views import View

from apps.audit.dtos import SecurityAction, SecurityStatus
from apps.audit.loggers.security_logger import SecurityLogger
from apps.twofactor.dtos import TwoFactorSetupDTO
from apps.twofactor.forms import TwoFactorCodeForm
from apps.twofactor.models import TwoFactorDevice
from apps.twofactor.services import (
    TwoFactorActivationError,
    TwoFactorActivationService,
    TwoFactorEmailCodeService,
    TwoFactorSetupService,
)


class TwoFactorSetupView(LoginRequiredMixin, View):
    template_name = "twofactor/setup.html"
    recovery_codes_template_name = "twofactor/recovery_codes.html"

    def get(self, request):
        if self._already_enabled(request.user):
            messages.info(request, _("Two-factor authentication is already enabled."))
            return redirect("account:settings")

        if not TwoFactorSetupService.is_email_available():
            messages.error(request, self._not_configured_message())
            return redirect("account:settings")

        setup = self._send_first_code(request)
        return render(request, self.template_name, self._context(setup, TwoFactorCodeForm()))

    def post(self, request):
        if self._already_enabled(request.user):
            return redirect("account:settings")

        if request.POST.get("action") == "resend":
            return self._resend(request)

        return self._confirm(request)

    def _send_first_code(self, request) -> TwoFactorSetupDTO:
        try:
            return TwoFactorSetupService.start(request.user)
        except Exception:
            messages.error(request, self._send_failed_message())
            return self._current_setup_dto(request.user)

    def _resend(self, request):
        if not TwoFactorSetupService.is_email_available():
            messages.error(request, self._not_configured_message())
            return redirect("account:settings")

        try:
            setup = TwoFactorSetupService.resend(request.user)
            messages.success(request, _("A new code was sent to your email."))
        except Exception:
            messages.error(request, self._send_failed_message())
            setup = self._current_setup_dto(request.user)

        return render(request, self.template_name, self._context(setup, TwoFactorCodeForm()))

    def _confirm(self, request):
        form = TwoFactorCodeForm(request.POST)
        setup = self._current_setup_dto(request.user)

        if not form.is_valid():
            return render(request, self.template_name, self._context(setup, form))

        try:
            recovery_codes = TwoFactorActivationService.activate(request.user, form.cleaned_data["code"])
        except TwoFactorActivationError as error:
            form.add_error("code", str(error))
            self._log(request, SecurityStatus.FAILED, "Invalid code while confirming 2FA setup")
            return render(request, self.template_name, self._context(setup, form))

        self._log(request, SecurityStatus.SUCCESS, "2FA enabled")
        return render(request, self.recovery_codes_template_name, {"recovery_codes": recovery_codes})

    def _current_setup_dto(self, user) -> TwoFactorSetupDTO:
        return TwoFactorSetupDTO(masked_email=TwoFactorEmailCodeService.mask_email(user.email))

    def _already_enabled(self, user) -> bool:
        return TwoFactorDevice.objects.filter(user=user, confirmed=True).exists()

    def _context(self, setup, form):
        return {"setup": setup, "form": form}

    def _not_configured_message(self):
        return _(
            "Two-factor authentication is unavailable until an administrator configures "
            "the system's email server."
        )

    def _send_failed_message(self):
        return _("We couldn't send the verification email right now. Please try again in a moment.")

    def _log(self, request, status, reason):
        SecurityLogger.log_event(
            user=request.user,
            ip_address=request.META.get("REMOTE_ADDR"),
            action=SecurityAction.MFA_ENABLED,
            status=status,
            reason=reason,
        )
