from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import ngettext
from django.views import View

from apps.inventory.forms.item_import_form import ItemImportForm
from apps.inventory.services.item_import import import_items_from_csv
from apps.organizations.mixins import InventoryWriteRequiredMixin


class ItemImportView(LoginRequiredMixin, InventoryWriteRequiredMixin, View):
    template_name = "inventory/item_import.html"
    success_url = reverse_lazy("inventory:item_list")

    def get(self, request):
        return render(request, self.template_name, {"form": ItemImportForm()})

    def post(self, request):
        form = ItemImportForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        result = import_items_from_csv(request.organization, form.cleaned_data["csv_file"], request.user)

        if result.created_count:
            messages.success(
                request,
                ngettext(
                    "%(count)s item imported successfully.",
                    "%(count)s items imported successfully.",
                    result.created_count,
                )
                % {"count": result.created_count},
            )
        if result.has_errors:
            return render(request, self.template_name, {"form": ItemImportForm(), "result": result})

        return redirect(self.success_url)
