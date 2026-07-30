from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views import View

from apps.settings.mixins import StaffRequiredMixin
from apps.settings.models import EmailSettings

from ..forms import EmailSettingsForm


class EmailSettingsView(LoginRequiredMixin, StaffRequiredMixin, View):
    template_name = "settings/email_settings.html"

    def get(self, request):
        form = EmailSettingsForm(instance=EmailSettings.load())
        return render(request, self.template_name, self._context(form))

    def post(self, request):
        form = EmailSettingsForm(request.POST, instance=EmailSettings.load())
        if not form.is_valid():
            return render(request, self.template_name, self._context(form))

        email_settings = form.save(commit=False)
        email_settings.updated_by = request.user
        email_settings.save()

        messages.success(request, _("Email settings updated successfully."))
        return redirect(request.POST.get("next") or "settings:email_settings")

    def _context(self, form):
        return {"form": form}
