from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.views import View

from apps.organizations.mixins import MemberManagementRequiredMixin
from apps.organizations.models import ASSIGNABLE_MEMBERSHIP_ROLES, Membership, MembershipRole


class MemberRoleUpdateView(LoginRequiredMixin, MemberManagementRequiredMixin, View):
    def post(self, request, membership_id):
        membership = get_object_or_404(Membership, id=membership_id, organization=request.organization)

        if membership.user_id == request.user.id:
            messages.error(request, _("You can't change your own role."))
            return redirect("organizations:members")

        if membership.role == MembershipRole.OWNER:
            messages.error(request, _("The organization owner's role can't be changed."))
            return redirect("organizations:members")

        new_role = request.POST.get("role")
        if new_role not in ASSIGNABLE_MEMBERSHIP_ROLES:
            messages.error(request, _("Invalid role."))
            return redirect("organizations:members")

        membership.role = new_role
        membership.updated_by = request.user
        membership.save()
        messages.success(request, _("Role updated successfully."))
        return redirect("organizations:members")
