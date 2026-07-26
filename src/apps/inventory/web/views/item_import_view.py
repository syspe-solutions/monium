import csv

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import ngettext
from django.views import View

from apps.inventory.forms.item_import_form import ItemImportForm
from apps.inventory.services.item_import import IMPORT_COLUMNS, import_items_from_csv
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


class ItemImportTemplateView(LoginRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="modelo-importacao-itens.csv"'
        response.write("﻿")

        writer = csv.writer(response, delimiter=";")
        writer.writerow(IMPORT_COLUMNS)
        writer.writerow([
            "PAT-0001", "Notebook Dell Inspiron 15", "Equipamentos de TI", "Financeiro",
            "Sala 2", "Dell", "Maria Souza", "Em uso", "Bom",
        ])
        return response
