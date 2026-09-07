from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views import View

from apps.inventory.forms.real_estate_form import RealEstateForm
from apps.organizations.mixins import InventoryWriteRequiredMixin


class RealEstateCreateView(LoginRequiredMixin, InventoryWriteRequiredMixin, View):
    template_name = "inventory/real_estate_form.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RealEstateForm()})

    def post(self, request):
        form = RealEstateForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        organization = request.organization
        real_estate = form.save(commit=False)
        real_estate.organization = organization
        real_estate.created_by = request.user
        real_estate.updated_by = request.user
        real_estate.save()

        messages.success(
            request, _('Real estate "%(name)s" registered successfully.') % {"name": real_estate.name}
        )
        return redirect("inventory:real_estate_detail", pk=real_estate.id)
