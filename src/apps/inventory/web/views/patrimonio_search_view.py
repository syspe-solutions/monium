from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse
from django.views import View

from apps.inventory.services.patrimonio_filters import filter_patrimonios, to_rows

SEARCH_RESULTS_LIMIT = 8


class PatrimonioSearchView(LoginRequiredMixin, View):
    def get(self, request):
        query = (request.GET.get("q") or "").strip()
        if not query:
            return JsonResponse({"results": []})

        items = filter_patrimonios(request.organization, {"q": query})[:SEARCH_RESULTS_LIMIT]
        rows = to_rows(items)

        return JsonResponse({"results": [self._serialize(row) for row in rows]})

    def _serialize(self, row):
        return {
            "name": row.item.name,
            "code": row.item.code,
            "tipo": row.tipo,
            "tipo_label": str(row.tipo_label),
            "categoria": row.categoria_nome,
            "url": reverse(row.detail_url_name, args=[row.item.pk]),
        }
