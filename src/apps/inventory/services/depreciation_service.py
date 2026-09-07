from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from django.utils import timezone

from apps.inventory.models import Acquisition


@dataclass
class DepreciationResult:
    acquisition_value: Decimal
    current_book_value: Decimal
    accumulated_depreciation: Decimal
    depreciation_percent: Decimal
    useful_life_months: Optional[int]
    elapsed_months: int
    is_depreciable: bool
    is_fully_depreciated: bool


def calculate_depreciation(
    acquisition: Acquisition,
    as_of: Optional[date] = None,
    useful_life_months: Optional[int] = None,
) -> Optional[DepreciationResult]:
    """Depreciação linear com base na vida útil cadastrada na categoria do item
    (apps.inventory.models.Category.useful_life_months). Sem valor ou data de
    compra não há o que calcular (None). Sem vida útil configurada, ainda
    retorna um resultado "não depreciável" — valor atual = valor de aquisição
    — pra que somatórios de carteira não precisem tratar esse caso à parte.

    `useful_life_months` pode ser passado explicitamente por quem já tem a
    categoria do item em mãos (ex.: página de detalhe, que já fez
    select_related nela) — evita as duas queries extras que
    `acquisition.item.movable_asset.category` disparia pra descobrir de novo algo que
    o chamador já sabe."""

    if acquisition.value is None or acquisition.purchase_date is None:
        return None

    if useful_life_months is None:
        useful_life_months = _resolve_useful_life_months(acquisition.item)

    if not useful_life_months:
        return DepreciationResult(
            acquisition_value=acquisition.value,
            current_book_value=acquisition.value,
            accumulated_depreciation=Decimal("0"),
            depreciation_percent=Decimal("0"),
            useful_life_months=None,
            elapsed_months=0,
            is_depreciable=False,
            is_fully_depreciated=False,
        )

    elapsed_months = _clamp(
        _months_between(acquisition.purchase_date, as_of or timezone.now().date()),
        minimum=0,
        maximum=useful_life_months,
    )

    monthly_depreciation = acquisition.value / useful_life_months
    accumulated = min((monthly_depreciation * elapsed_months).quantize(Decimal("0.01")), acquisition.value)
    current_book_value = acquisition.value - accumulated
    percent = (accumulated / acquisition.value * 100) if acquisition.value else Decimal("0")

    return DepreciationResult(
        acquisition_value=acquisition.value,
        current_book_value=current_book_value,
        accumulated_depreciation=accumulated,
        depreciation_percent=percent.quantize(Decimal("0.1")),
        useful_life_months=useful_life_months,
        elapsed_months=elapsed_months,
        is_depreciable=True,
        is_fully_depreciated=elapsed_months >= useful_life_months,
    )


def _resolve_useful_life_months(item) -> Optional[int]:
    movable_asset = getattr(item, "movable_asset", None)
    if movable_asset is None:
        return None
    return movable_asset.category.useful_life_months


def _months_between(start: date, end: date) -> int:
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return months


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(value, maximum))
