from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views import View

from apps.organizations.middleware import ACTIVE_ORG_SESSION_KEY
from apps.organizations.models import Membership, MembershipRole

from ..forms import OrganizationForm


class OrganizationCreateView(LoginRequiredMixin, View):
    template_name = "organizations/create.html"

    def get(self, request):
        is_first = request.user.organization is None
        return render(request, self.template_name, {"form": OrganizationForm(), "is_first": is_first})

    def post(self, request):
        is_first = request.user.organization is None
        form = OrganizationForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "is_first": is_first})

        organization = form.save(commit=False)
        organization.created_by = request.user
        organization.updated_by = request.user
        organization.save()
        Membership.objects.create(
            organization=organization,
            user=request.user,
            role=MembershipRole.OWNER,
            created_by=request.user,
        )
        request.session[ACTIVE_ORG_SESSION_KEY] = str(organization.id)

        messages.success(
            request, _('Organization "%(name)s" created successfully.') % {"name": organization.name}
        )
        return redirect("inventory:home")
