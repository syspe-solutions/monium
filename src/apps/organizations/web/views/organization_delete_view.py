from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views import View

from apps.organizations.middleware import ACTIVE_ORG_SESSION_KEY
from apps.organizations.models import Membership, MembershipRole


class OrganizationDeleteView(LoginRequiredMixin, View):
    template_name = "organizations/delete_confirm.html"

    def _get_organization_or_404(self, request, organization_id):
        return get_object_or_404(
            Membership, organization_id=organization_id, user=request.user, role=MembershipRole.OWNER
        ).organization

    def get(self, request, organization_id):
        organization = self._get_organization_or_404(request, organization_id)
        return render(request, self.template_name, {"organization": organization})

    def post(self, request, organization_id):
        organization = self._get_organization_or_404(request, organization_id)

        owned_count = Membership.objects.filter(
            user=request.user, role=MembershipRole.OWNER
        ).count()
        if owned_count <= 1:
            messages.error(request, _("You need to have at least one organization."))
            return redirect("organizations:settings")

        confirmation = request.POST.get("confirmation_name", "").strip()
        if confirmation != organization.name:
            messages.error(request, _("The typed name doesn't match. The organization was not deleted."))
            return render(request, self.template_name, {"organization": organization})

        name = organization.name
        organization.delete()

        if request.session.get(ACTIVE_ORG_SESSION_KEY) == str(organization_id):
            del request.session[ACTIVE_ORG_SESSION_KEY]

        messages.success(request, _('Organization "%(name)s" deleted.') % {"name": name})
        return redirect("inventory:home")
