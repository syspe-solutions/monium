from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views import View

from apps.inventory.forms.imovel_form import ImovelForm
from apps.inventory.models import Imovel
from apps.organizations.mixins import InventoryWriteRequiredMixin


class ImovelUpdateView(LoginRequiredMixin, InventoryWriteRequiredMixin, View):
    template_name = "inventory/imovel_form.html"

    def _get_imovel(self, request, pk):
        return get_object_or_404(
            Imovel.objects.select_related("category"),
            pk=pk,
            organization=request.organization,
        )

    def get(self, request, pk):
        imovel = self._get_imovel(request, pk)
        return render(request, self.template_name, {"imovel": imovel, "form": ImovelForm(instance=imovel)})

    def post(self, request, pk):
        imovel = self._get_imovel(request, pk)
        form = ImovelForm(request.POST, instance=imovel)
        if not form.is_valid():
            return render(request, self.template_name, {"imovel": imovel, "form": form})

        imovel = form.save(commit=False)
        imovel.updated_by = request.user
        imovel.save()

        messages.success(
            request, _('Real estate "%(name)s" updated successfully.') % {"name": imovel.name}
        )
        return redirect("inventory:imovel_detail", pk=imovel.id)
