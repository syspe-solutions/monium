from django.db.models import Q, QuerySet

from apps.inventory.models import Imovel


def filter_imoveis(organization, filters: dict) -> QuerySet:
    imoveis = Imovel.objects.filter(organization=organization).select_related("category")

    query = (filters.get("q") or "").strip()
    if query:
        imoveis = imoveis.filter(
            Q(name__icontains=query) | Q(code__icontains=query) | Q(address__icontains=query)
        )

    if filters.get("category"):
        imoveis = imoveis.filter(category=filters["category"])

    if filters.get("zone"):
        imoveis = imoveis.filter(zone=filters["zone"])

    if filters.get("cartorio_situacao"):
        imoveis = imoveis.filter(cartorio_situacao=filters["cartorio_situacao"])

    return imoveis
