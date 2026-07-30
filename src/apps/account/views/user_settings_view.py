from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.settings.models import EmailSettings
from apps.settings.web.forms import EmailSettingsForm


class UserSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "account/settings/settings.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            ctx["email_form"] = EmailSettingsForm(instance=EmailSettings.load())
        return ctx
