from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.views import View

from apps.organizations.mixins import MemberManagementRequiredMixin
from apps.organizations.models import Membership, MembershipRole


class MemberRemoveView(LoginRequiredMixin, MemberManagementRequiredMixin, View):
    def post(self, request, membership_id):
        membership = get_object_or_404(Membership, id=membership_id, organization=request.organization)

        if membership.user_id == request.user.id:
            messages.error(request, _("You can't remove yourself from the organization."))
            return redirect("organizations:members")

        if membership.role == MembershipRole.OWNER:
            messages.error(request, _("The organization owner can't be removed."))
            return redirect("organizations:members")

        if request.organization.memberships.count() <= 1:
            messages.error(request, _("The organization needs to have at least one member."))
            return redirect("organizations:members")

        membership.delete()
        messages.success(request, _("Member removed from the organization."))
        return redirect("organizations:members")
