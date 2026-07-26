from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views import View

from apps.inventory.forms.imovel_form import ImovelForm
from apps.organizations.mixins import InventoryWriteRequiredMixin


class ImovelCreateView(LoginRequiredMixin, InventoryWriteRequiredMixin, View):
    template_name = "inventory/imovel_form.html"
    success_url = reverse_lazy("inventory:imovel_list")

    def get(self, request):
        return render(request, self.template_name, {"form": ImovelForm()})

    def post(self, request):
        form = ImovelForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        organization = request.organization
        imovel = form.save(commit=False)
        imovel.organization = organization
        imovel.created_by = request.user
        imovel.updated_by = request.user
        imovel.save()

        messages.success(
            request, _('Real estate "%(name)s" registered successfully.') % {"name": imovel.name}
        )
        return redirect(self.success_url)
