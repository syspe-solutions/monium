from django import template

from apps.inventory.models import LoanStatus, MovelStatus

register = template.Library()

_STATUS_BADGE_CLASSES = {
    MovelStatus.IN_USE: "bg-green-950 text-green-400",
    MovelStatus.STORED: "bg-blue-950 text-blue-400",
    MovelStatus.MAINTENANCE: "bg-amber-950 text-amber-400",
    MovelStatus.MISSING: "bg-red-950 text-red-400",
    MovelStatus.DISCARDED: "bg-zinc-800 text-zinc-400",
}
_DEFAULT_BADGE_CLASSES = "bg-zinc-800 text-zinc-400"

_LOAN_STATUS_BADGE_CLASSES = {
    LoanStatus.ACTIVE: "bg-blue-950 text-blue-400",
    LoanStatus.RETURNED: "bg-zinc-800 text-zinc-400",
    LoanStatus.OVERDUE: "bg-red-950 text-red-400",
}

_TIPO_BADGE_CLASSES = {
    "movel": "bg-blue-950 text-blue-400",
    "imovel": "bg-purple-950 text-purple-400",
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
