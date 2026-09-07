from difflib import SequenceMatcher

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.views import View

from apps.inventory.models import Brand

SIMILARITY_THRESHOLD = 0.80

NEW_BRAND_OPTION = "__new__"


def find_similar_brands(name: str) -> list[tuple[Brand, float]]:
    normalized = name.lower().strip()
    results = []
    for brand in Brand.objects.all():
        ratio = SequenceMatcher(None, normalized, brand.name.lower().strip()).ratio()
        if ratio >= SIMILARITY_THRESHOLD:
            results.append((brand, ratio))
    return sorted(results, key=lambda x: x[1], reverse=True)


def resolve_brand(brand_id: str, new_brand_name: str, created_by) -> tuple[Brand | None, str]:
    """Resolve o Brand escolhido no formulário de item: reaproveita um já
    cadastrado pelo id, cria um novo (se não houver nome muito parecido já
    existente), ou não retorna nenhum se nada foi informado.

    Usado tanto na criação quanto na edição de itens — antes só existia
    dentro do MovableAssetCreateView.
    """
    if brand_id and brand_id != NEW_BRAND_OPTION:
        try:
            return Brand.objects.get(id=brand_id), ""
        except Brand.DoesNotExist:
            return None, _("Selected brand not found.")

    if not new_brand_name:
        return None, ""

    similar = find_similar_brands(new_brand_name)
    if similar:
        closest = similar[0][0].name
        error = _(
            'A very similar brand already exists: "%(name)s". Select it from the list or choose a '
            "different name."
        ) % {"name": closest}
        return None, error

    brand = Brand.objects.create(name=new_brand_name, created_by=created_by, updated_by=created_by)
    return brand, ""


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
