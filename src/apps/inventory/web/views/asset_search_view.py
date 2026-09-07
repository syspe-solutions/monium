from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse
from django.views import View

from apps.inventory.services.asset_filters import filter_assets, to_rows

SEARCH_RESULTS_LIMIT = 8


class AssetSearchView(LoginRequiredMixin, View):
    def get(self, request):
        query = (request.GET.get("q") or "").strip()
        if not query:
            return JsonResponse({"results": []})

        items = filter_assets(request.organization, {"q": query})[:SEARCH_RESULTS_LIMIT]
        rows = to_rows(items)

        return JsonResponse({"results": [self._serialize(row) for row in rows]})

    def _serialize(self, row):
        return {
            "name": row.item.name,
            "code": row.item.code,
            "asset_type": row.asset_type,
            "asset_type_label": str(row.asset_type_label),
            "category": row.category_name,
            "url": reverse(row.detail_url_name, args=[row.item.pk]),
        }
