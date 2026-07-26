from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views import View

from apps.organizations.middleware import ACTIVE_ORG_SESSION_KEY
from apps.organizations.models import Membership


class SwitchOrganizationView(LoginRequiredMixin, View):
    def post(self, request, organization_id):
        is_member = Membership.objects.filter(organization_id=organization_id, user=request.user).exists()
        if not is_member:
            raise PermissionDenied(_("You're not a member of this organization."))

        request.session[ACTIVE_ORG_SESSION_KEY] = str(organization_id)

        next_url = request.POST.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect("inventory:home")
