from decimal import Decimal, InvalidOperation

from django import template

from apps.inventory.models import LoanStatus, MovelStatus

register = template.Library()

_STATUS_BADGE_CLASSES = {
    MovelStatus.IN_USE: "bg-green-50 text-green-600",
    MovelStatus.STORED: "bg-accent-subtle text-accent",
    MovelStatus.MAINTENANCE: "bg-amber-50 text-amber-600",
    MovelStatus.MISSING: "bg-red-50 text-red-600",
    MovelStatus.DISCARDED: "bg-zinc-100 text-zinc-500",
}
_DEFAULT_BADGE_CLASSES = "bg-zinc-100 text-zinc-500"

_LOAN_STATUS_BADGE_CLASSES = {
    LoanStatus.ACTIVE: "bg-accent-subtle text-accent",
    LoanStatus.RETURNED: "bg-zinc-100 text-zinc-500",
    LoanStatus.OVERDUE: "bg-red-50 text-red-600",
}

_TIPO_BADGE_CLASSES = {
    "movel": "bg-accent-subtle text-accent",
    "imovel": "bg-purple-50 text-purple-600",
}


@register.filter
def status_badge_class(status: str) -> str:
    """Mapeia um valor de MovelStatus para as classes Tailwind do badge correspondente."""
    return _STATUS_BADGE_CLASSES.get(status, _DEFAULT_BADGE_CLASSES)


@register.filter
def loan_status_badge_class(status: str) -> str:
    """Mapeia um valor de LoanStatus para as classes Tailwind do badge correspondente."""
    return _LOAN_STATUS_BADGE_CLASSES.get(status, _DEFAULT_BADGE_CLASSES)


@register.filter
def tipo_badge_class(tipo: str) -> str:
    """Mapeia "movel"/"imovel" para as classes Tailwind do badge correspondente."""
    return _TIPO_BADGE_CLASSES.get(tipo, _DEFAULT_BADGE_CLASSES)


@register.filter
def brl(value) -> str:
    """Formata um valor monetário como R$ 1.234,56 (pt-BR)."""
    try:
        value = Decimal(value)
    except (InvalidOperation, TypeError):
        return "R$ 0,00"
    formatted = f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"
