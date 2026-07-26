import logging
from dataclasses import dataclass

from django.db.models import Q, QuerySet
from django.utils.translation import gettext as _

from apps.inventory.models import Item

logger = logging.getLogger(__name__)


@dataclass
class PatrimonioRow:
    item: Item
    tipo: str
    tipo_label: str
    categoria_nome: str
    detail_url_name: str


def filter_patrimonios(organization, filters: dict) -> QuerySet:
    items = (
        Item.objects.filter(organization=organization)
        .filter(Q(movel__isnull=False) | Q(imovel__isnull=False))
        .select_related("movel__category", "imovel__category")
    )

    query = (filters.get("q") or "").strip()
    if query:
        items = items.filter(Q(name__icontains=query) | Q(code__icontains=query))

    tipo = filters.get("tipo")
    if tipo == "movel":
        items = items.filter(movel__isnull=False)
    elif tipo == "imovel":
        items = items.filter(imovel__isnull=False)

    if filters.get("condition"):
        items = items.filter(condition=filters["condition"])

    return items.order_by("name")


def to_rows(items) -> list[PatrimonioRow]:
    rows = []
    for item in items:
        if hasattr(item, "movel"):
            rows.append(
                PatrimonioRow(
                    item=item,
                    tipo="movel",
                    tipo_label=_("Item"),
                    categoria_nome=item.movel.category.name,
                    detail_url_name="inventory:item_detail",
                )
            )
        elif hasattr(item, "imovel"):
            rows.append(
                PatrimonioRow(
                    item=item,
                    tipo="imovel",
                    tipo_label=_("Real Estate"),
                    categoria_nome=item.imovel.category.name,
                    detail_url_name="inventory:imovel_detail",
                )
            )
        else:
            logger.warning("Item %s has neither a Movel nor an Imovel — skipping from Patrimônios list.", item.id)
    return rows
