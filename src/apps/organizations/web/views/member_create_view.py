from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views import View

from apps.organizations.mixins import MemberManagementRequiredMixin

from ..forms import MemberCreateForm


class MemberCreateView(LoginRequiredMixin, MemberManagementRequiredMixin, View):
    template_name = "organizations/member_create.html"

    def get(self, request):
        form = MemberCreateForm(organization=request.organization)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = MemberCreateForm(request.POST, organization=request.organization)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        membership = form.save(created_by=request.user)
        messages.success(
            request, _('User "%(email)s" created successfully.') % {"email": membership.user.email}
        )
        return redirect("organizations:settings")
