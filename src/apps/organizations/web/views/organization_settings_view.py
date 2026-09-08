from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views import View

from apps.organizations.mixins import MemberManagementRequiredMixin
from apps.organizations.models import ASSIGNABLE_MEMBERSHIP_ROLES, Membership, MembershipRole

from ..forms import OrganizationForm


class OrganizationSettingsView(LoginRequiredMixin, MemberManagementRequiredMixin, View):
    """Página única de configurações da organização + gestão de membros.

    A listagem de membros é visível a OWNER e ADMIN (mesmo requisito do
    MemberManagementRequiredMixin que já controla o acesso à view). Editar os
    dados da organização continua restrito a OWNER — o formulário só é
    montado pra quem tem essa permissão, e o POST é bloqueado no servidor
    pros demais, independente do que o template renderiza.
    """

    template_name = "organizations/settings.html"

    def _context(self, form):
        organization = self.request.organization
        return {
            "form": form,
            "members": organization.memberships.select_related("user").order_by("role", "user__email"),
            "assignable_roles": ASSIGNABLE_MEMBERSHIP_ROLES,
        }

    def get(self, request):
        form = OrganizationForm(instance=request.organization) if self._is_owner(request) else None
        return render(request, self.template_name, self._context(form))

    def post(self, request):
        if not self._is_owner(request):
            raise PermissionDenied(_("Only the organization owner can edit these settings."))

        form = OrganizationForm(request.POST, request.FILES, instance=request.organization)
        if not form.is_valid():
            return render(request, self.template_name, self._context(form))

        organization = form.save(commit=False)
        organization.updated_by = request.user
        organization.save()

        messages.success(request, _("Organization data updated successfully."))
        return redirect("organizations:settings")

    def _is_owner(self, request):
        return Membership.objects.filter(
            organization=request.organization, user=request.user, role=MembershipRole.OWNER
        ).exists()
