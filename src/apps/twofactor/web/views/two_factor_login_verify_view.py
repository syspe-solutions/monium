from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views import View

from apps.audit.dtos import SecurityAction, SecurityStatus
from apps.audit.loggers.security_logger import SecurityLogger
from apps.twofactor.dtos import TwoFactorSetupDTO
from apps.twofactor.forms import TwoFactorCodeForm
from apps.twofactor.services import (
    TwoFactorEmailCodeService,
    TwoFactorLoginChallengeService,
    TwoFactorVerificationService,
)


class TwoFactorLoginVerifyView(View):
    """Segundo passo do login quando o usuário tem 2FA confirmado — a senha já
    foi validada por UserLoginView, mas django.contrib.auth.login() só é
    chamado aqui, depois do código confirmado. Ver TwoFactorLoginChallengeService
    pra como o usuário pendente atravessa o redirect sem sessão autenticada."""

    template_name = "twofactor/login_verify.html"

    def get(self, request):
        pending_user = TwoFactorLoginChallengeService.get_pending_user(request)
        if not pending_user:
            return redirect("account:login")

        if not TwoFactorLoginChallengeService.code_already_sent(request):
            self._send_code(request, pending_user)

        return render(request, self.template_name, self._context(pending_user, TwoFactorCodeForm()))

    def post(self, request):
        pending_user = TwoFactorLoginChallengeService.get_pending_user(request)
        if not pending_user:
            return redirect("account:login")

        if request.POST.get("action") == "resend":
            return self._resend(request, pending_user)

        form = TwoFactorCodeForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, self._context(pending_user, form))

        device = getattr(pending_user, "two_factor_device", None)
        verified = (
            device is not None
            and device.confirmed
            and TwoFactorVerificationService.verify(device, form.cleaned_data["code"])
        )

        if not verified:
            return self._handle_failure(request, pending_user, form)

        return self._complete_login(request, pending_user)

    def _send_code(self, request, user):
        device = getattr(user, "two_factor_device", None)
        if device is None:
            return
        try:
            TwoFactorEmailCodeService.send(device)
        except Exception:
            messages.error(
                request,
                _("We couldn't send the verification email right now. You can still use a recovery code."),
            )
        finally:
            TwoFactorLoginChallengeService.mark_code_sent(request)

    def _resend(self, request, user):
        remaining = TwoFactorLoginChallengeService.seconds_until_resend_allowed(request)
        if remaining > 0:
            messages.error(request, _("Please wait a moment before requesting another code."))
        else:
            self._send_code(request, user)
            messages.success(request, _("A new code was sent to your email."))

        return render(request, self.template_name, self._context(user, TwoFactorCodeForm()))

    def _complete_login(self, request, user):
        backend = TwoFactorLoginChallengeService.get_backend(request)
        next_url = TwoFactorLoginChallengeService.get_next_url(request)
        TwoFactorLoginChallengeService.clear(request)

        login(request, user, backend=backend)
        self._log(request, user, SecurityStatus.SUCCESS, SecurityAction.MFA_VERIFIED, "2FA code accepted at login")

        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect("inventory:home")

    def _handle_failure(self, request, user, form):
        self._log(request, user, SecurityStatus.FAILED, SecurityAction.MFA_FAILED, "Invalid 2FA code at login")

        if TwoFactorLoginChallengeService.register_failed_attempt(request) >= TwoFactorLoginChallengeService.MAX_ATTEMPTS:
            TwoFactorLoginChallengeService.clear(request)
            messages.error(request, _("Too many failed attempts. Please sign in again."))
            return redirect("account:login")

        form.add_error("code", _("Invalid code. Please try again."))
        return render(request, self.template_name, self._context(user, form))

    def _context(self, user, form):
        return {
            "form": form,
            "setup": TwoFactorSetupDTO(masked_email=TwoFactorEmailCodeService.mask_email(user.email)),
        }

    def _log(self, request, user, status, action, reason):
        SecurityLogger.log_event(
            user=user,
            ip_address=request.META.get("REMOTE_ADDR"),
            action=action,
            status=status,
            reason=reason,
        )
