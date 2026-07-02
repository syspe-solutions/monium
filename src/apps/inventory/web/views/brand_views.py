from difflib import SequenceMatcher

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from apps.inventory.models import Brand

SIMILARITY_THRESHOLD = 0.80


def find_similar_brands(name: str) -> list[tuple[Brand, float]]:
    normalized = name.lower().strip()
    results = []
    for brand in Brand.objects.all():
        ratio = SequenceMatcher(None, normalized, brand.name.lower().strip()).ratio()
        if ratio >= SIMILARITY_THRESHOLD:
            results.append((brand, ratio))
    return sorted(results, key=lambda x: x[1], reverse=True)


class BrandSimilarityCheckView(LoginRequiredMixin, View):
    def get(self, request):
        name = request.GET.get("name", "").strip()
        if not name:
            return JsonResponse({"similar": []})
        similar = find_similar_brands(name)
        return JsonResponse({
            "similar": [
                {"id": str(b.id), "name": b.name, "ratio": round(r * 100)}
                for b, r in similar
            ]
        })
