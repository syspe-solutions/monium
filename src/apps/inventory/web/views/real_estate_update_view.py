from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views import View

from apps.inventory.forms.real_estate_form import RealEstateForm
from apps.inventory.models import RealEstateAsset
from apps.organizations.mixins import InventoryWriteRequiredMixin


class RealEstateUpdateView(LoginRequiredMixin, InventoryWriteRequiredMixin, View):
    template_name = "inventory/real_estate_form.html"

    def _get_real_estate(self, request, pk):
        return get_object_or_404(
            RealEstateAsset.objects.select_related("category"),
            pk=pk,
            organization=request.organization,
        )

    def get(self, request, pk):
        real_estate = self._get_real_estate(request, pk)
        return render(request, self.template_name, {"real_estate": real_estate, "form": RealEstateForm(instance=real_estate)})

    def post(self, request, pk):
        real_estate = self._get_real_estate(request, pk)
        form = RealEstateForm(request.POST, instance=real_estate)
        if not form.is_valid():
            return render(request, self.template_name, {"real_estate": real_estate, "form": form})

        real_estate = form.save(commit=False)
        real_estate.updated_by = request.user
        real_estate.save()

        messages.success(
            request, _('Real estate "%(name)s" updated successfully.') % {"name": real_estate.name}
        )
        return redirect("inventory:real_estate_detail", pk=real_estate.id)
