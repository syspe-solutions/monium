from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from apps.billing import services as billing_services
from apps.inventory.forms.imovel_form import ImovelForm
from apps.organizations.mixins import OrganizationNotLockedRequiredMixin


class ImovelCreateView(LoginRequiredMixin, OrganizationNotLockedRequiredMixin, View):
    template_name = "inventory/imovel_form.html"
    success_url = reverse_lazy("inventory:imovel_list")

    def get(self, request):
        return render(request, self.template_name, {"form": ImovelForm()})

    def post(self, request):
        form = ImovelForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        organization = request.organization
        if not billing_services.is_within_item_limit(organization):
            messages.error(
                request,
                "Você atingiu o limite de itens do seu plano atual. Faça upgrade para continuar cadastrando.",
            )
            return redirect("billing:plans")

        imovel = form.save(commit=False)
        imovel.organization = organization
        imovel.created_by = request.user
        imovel.updated_by = request.user
        imovel.save()

        messages.success(request, f'Imóvel "{imovel.name}" cadastrado com sucesso.')
        return redirect(self.success_url)
