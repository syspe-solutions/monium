import csv

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import View

from apps.inventory.services.item_import import IMPORT_COLUMNS


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
