import csv

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.utils import timezone
from django.views import View

from apps.inventory.forms.movable_asset_filter_form import MovableAssetFilterForm
from apps.inventory.services.movable_asset_filters import filter_items


class MovableAssetExportView(LoginRequiredMixin, View):
    def get(self, request):
        organization = request.organization
        form = MovableAssetFilterForm(request.GET or None)
        filters = form.cleaned_data if form.is_valid() else {}
        items = filter_items(organization, filters)

        filename = f"itens-{timezone.now():%Y%m%d-%H%M}.csv"
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write("﻿")  # BOM so Excel opens the UTF-8 CSV with accents intact

        writer = csv.writer(response, delimiter=";")
        writer.writerow([
            "Código", "Nome", "Categoria", "Setor", "Localização",
            "Marca", "Responsável", "Status", "Condição", "Cadastrado em",
        ])
        for item in items:
            spec = getattr(item, "spec", None)
            writer.writerow([
                item.code,
                item.name,
                item.category.name,
                item.sector.name,
                item.location.name if item.location else "",
                spec.brand.name if spec and spec.brand else "",
                item.responsible,
                item.get_status_display(),
                item.get_condition_display(),
                item.created_at.strftime("%d/%m/%Y %H:%M"),
            ])

        return response
