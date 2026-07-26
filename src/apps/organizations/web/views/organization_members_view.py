from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.organizations.mixins import MemberManagementRequiredMixin
from apps.organizations.models import ASSIGNABLE_MEMBERSHIP_ROLES


class OrganizationMembersView(LoginRequiredMixin, MemberManagementRequiredMixin, TemplateView):
    template_name = "organizations/members.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        organization = self.request.organization
        ctx["members"] = organization.memberships.select_related("user").order_by("role", "user__email")
        ctx["assignable_roles"] = ASSIGNABLE_MEMBERSHIP_ROLES
        return ctx
