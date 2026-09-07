from django.db.models import Q, QuerySet

from apps.inventory.models import RealEstateAsset


def filter_real_estate_assets(organization, filters: dict) -> QuerySet:
    real_estate_assets = RealEstateAsset.objects.filter(organization=organization).select_related("category")

    query = (filters.get("q") or "").strip()
    if query:
        real_estate_assets = real_estate_assets.filter(
            Q(name__icontains=query) | Q(code__icontains=query) | Q(address__icontains=query)
        )

    if filters.get("category"):
        real_estate_assets = real_estate_assets.filter(category=filters["category"])

    if filters.get("zone"):
        real_estate_assets = real_estate_assets.filter(zone=filters["zone"])

    if filters.get("cartorio_situacao"):
        real_estate_assets = real_estate_assets.filter(cartorio_situacao=filters["cartorio_situacao"])

    return real_estate_assets
