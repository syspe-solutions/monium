from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views import View

from apps.organizations.mixins import OrganizationOwnerRequiredMixin

from ..forms import OrganizationForm


class OrganizationSettingsView(LoginRequiredMixin, OrganizationOwnerRequiredMixin, View):
    template_name = "organizations/settings.html"

    def _context(self, form):
        organization = form.instance
        return {
            "form": form,
            "member_count": organization.memberships.count(),
        }

    def get(self, request):
        form = OrganizationForm(instance=request.organization)
        return render(request, self.template_name, self._context(form))

    def post(self, request):
        form = OrganizationForm(request.POST, instance=request.organization)
        if not form.is_valid():
            return render(request, self.template_name, self._context(form))

        organization = form.save(commit=False)
        organization.updated_by = request.user
        organization.save()

        messages.success(request, _("Organization data updated successfully."))
        return redirect("organizations:settings")
