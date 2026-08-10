from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views import View

from apps.audit.dtos import SecurityAction, SecurityStatus
from apps.audit.loggers.security_logger import SecurityLogger
from apps.settings.forms import EmailSettingsForm
from apps.settings.models import EmailSettings
from apps.twofactor.models import TwoFactorDevice
from apps.twofactor.services import TwoFactorSetupService


class UserSettingsView(LoginRequiredMixin, View):
    """Página única de configurações da conta. O formulário de e-mail (SMTP do
    sistema) é só staff, mas vive embutido aqui em vez de numa tela própria —
    não há mais rota separada pra isso."""

    template_name = "account/settings/settings.html"

    def get(self, request):
        return render(request, self.template_name, self._context(request))

    def post(self, request):
        if not request.user.is_staff:
            self._log_unauthorized(request)
            raise PermissionDenied

        form = EmailSettingsForm(request.POST, instance=EmailSettings.load())
        if not form.is_valid():
            return render(request, self.template_name, self._context(request, email_form=form))

        email_settings = form.save(commit=False)
        email_settings.updated_by = request.user
        email_settings.save()

        messages.success(request, _("Email settings updated successfully."))
        return redirect("account:settings")

    def _context(self, request, email_form=None):
        ctx = {
            "has_two_factor": TwoFactorDevice.objects.filter(
                user=request.user, confirmed=True
            ).exists(),
            "two_factor_email_available": TwoFactorSetupService.is_email_available(),
        }
        if request.user.is_staff:
            ctx["email_form"] = email_form or EmailSettingsForm(instance=EmailSettings.load())
        return ctx

    def _log_unauthorized(self, request):
        SecurityLogger.log_event(
            user=request.user,
            ip_address=request.META.get("REMOTE_ADDR"),
            action=SecurityAction.UNAUTHORIZED_ACCESS,
            status=SecurityStatus.FAILED,
            reason="User lacks staff permission to access system settings",
        )
