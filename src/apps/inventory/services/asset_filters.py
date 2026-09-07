import logging
from dataclasses import dataclass

from django.db.models import Q, QuerySet
from django.utils.translation import gettext as _

from apps.inventory.models import Item

logger = logging.getLogger(__name__)


@dataclass
class AssetRow:
    item: Item
    asset_type: str
    asset_type_label: str
    category_name: str
    detail_url_name: str


def filter_assets(organization, filters: dict) -> QuerySet:
    items = (
        Item.objects.filter(organization=organization)
        .filter(Q(movable_asset__isnull=False) | Q(real_estate_asset__isnull=False))
        .select_related("movable_asset__category", "real_estate_asset__category")
    )

    query = (filters.get("q") or "").strip()
    if query:
        items = items.filter(Q(name__icontains=query) | Q(code__icontains=query))

    asset_type = filters.get("asset_type")
    if asset_type == "movable_asset":
        items = items.filter(movable_asset__isnull=False)
    elif asset_type == "real_estate":
        items = items.filter(real_estate_asset__isnull=False)

    if filters.get("condition"):
        items = items.filter(condition=filters["condition"])

    return items.order_by("name")


def to_rows(items) -> list[AssetRow]:
    rows = []
    for item in items:
        if hasattr(item, "movable_asset"):
            rows.append(
                AssetRow(
                    item=item,
                    asset_type="movable_asset",
                    asset_type_label=_("Item"),
                    category_name=item.movable_asset.category.name,
                    detail_url_name="inventory:item_detail",
                )
            )
        elif hasattr(item, "real_estate_asset"):
            rows.append(
                AssetRow(
                    item=item,
                    asset_type="real_estate",
                    asset_type_label=_("Real Estate"),
                    category_name=item.real_estate_asset.category.name,
                    detail_url_name="inventory:real_estate_detail",
                )
            )
        else:
            logger.warning("Item %s has neither a MovableAsset nor a RealEstateAsset — skipping from assets list.", item.id)
    return rows
