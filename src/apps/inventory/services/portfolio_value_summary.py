from datetime import date
from decimal import Decimal

from django.db.models import Q, Sum
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone

from apps.inventory.models import Acquisition, Item
from apps.inventory.services.depreciation_service import calculate_depreciation
from apps.inventory.services.patrimonio_filters import to_rows


def get_portfolio_total_value(organization) -> Decimal:
    """Soma o valor de aquisição de todos os bens da organização (ausentes contam como 0)."""
    return Acquisition.objects.filter(item__organization=organization).aggregate(
        total=Coalesce(Sum("value"), Decimal("0"))
    )["total"]


def get_portfolio_current_value(organization) -> Decimal:
    """Soma o valor contábil atual (depreciado) dos bens da organização. Itens
    sem vida útil configurada na categoria entram pelo valor de aquisição —
    ver depreciation_service.calculate_depreciation."""
    acquisitions = (
        Acquisition.objects.filter(item__organization=organization, value__isnull=False)
        .select_related("item__movel__category")
    )
    total = Decimal("0")
    for acquisition in acquisitions:
        result = calculate_depreciation(acquisition)
        if result:
            total += result.current_book_value
    return total


def get_top_valued_items(organization, limit=5):
    """Bens com maior valor de aquisição cadastrado (itens sem valor não entram no ranking)."""
    items = (
        Item.objects.filter(organization=organization, acquisition__value__isnull=False)
        .filter(Q(movel__isnull=False) | Q(imovel__isnull=False))
        .select_related("acquisition", "movel__category", "imovel__category")
        .order_by("-acquisition__value")[:limit]
    )
    return to_rows(items)


def get_value_by_month(organization, months=6) -> dict:
    """Soma do valor de aquisição por mês de compra, últimos `months` meses (meses sem compra = 0)."""
    today = timezone.now().date()

    month_starts = []
    year, month = today.year, today.month
    for _ in range(months):
        month_starts.append(date(year, month, 1))
        month -= 1
        if month == 0:
            month, year = 12, year - 1
    month_starts.reverse()

    sums = (
        Acquisition.objects.filter(
            item__organization=organization,
            value__isnull=False,
            purchase_date__gte=month_starts[0],
        )
        .annotate(month=TruncMonth("purchase_date"))
        .values("month")
        .annotate(total=Sum("value"))
    )
    by_month = {row["month"]: row["total"] for row in sums}

    series = [{"month": month_start, "value": by_month.get(month_start, Decimal("0"))} for month_start in month_starts]
    max_value = max((point["value"] for point in series), default=Decimal("0"))

    return {"series": series, "max_value": max_value}
