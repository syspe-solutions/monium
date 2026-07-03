from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from apps.billing import services as billing_services
from apps.organizations.models import Membership, MembershipRole

from .forms import OrganizationForm


class OrganizationCreateView(LoginRequiredMixin, View):
    template_name = "organizations/create.html"

    def get(self, request):
        if request.user.organization is None:
            return render(request, self.template_name, {"form": OrganizationForm(), "is_first": True})

        if not billing_services.can_create_organization(request.user):
            messages.error(request, "Você atingiu o limite de organizações do seu plano. Faça upgrade para criar mais.")
            return redirect("billing:plans")

        return render(request, self.template_name, {"form": OrganizationForm(), "is_first": False})

    def post(self, request):
        is_first = request.user.organization is None
        if not is_first and not billing_services.can_create_organization(request.user):
            messages.error(request, "Você atingiu o limite de organizações do seu plano. Faça upgrade para criar mais.")
            return redirect("billing:plans")

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

        messages.success(request, f'Organização "{organization.name}" criada com sucesso.')
        return redirect("inventory:home")
