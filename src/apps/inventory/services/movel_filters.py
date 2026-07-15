from django.db.models import Q, QuerySet

from apps.inventory.models import Movel


def filter_items(organization, filters: dict) -> QuerySet:
    items = Movel.objects.filter(organization=organization).select_related(
        "category", "sector", "location"
    ).prefetch_related("spec__brand")

    query = (filters.get("q") or "").strip()
    if query:
        items = items.filter(
            Q(name__icontains=query) | Q(code__icontains=query) | Q(responsible__icontains=query)
        )

    if filters.get("status"):
        items = items.filter(status=filters["status"])

    if filters.get("condition"):
        items = items.filter(condition=filters["condition"])

    if filters.get("category"):
        items = items.filter(category=filters["category"])

    if filters.get("sector"):
        items = items.filter(sector=filters["sector"])

    if filters.get("brand"):
        items = items.filter(spec__brand=filters["brand"])

    return items
