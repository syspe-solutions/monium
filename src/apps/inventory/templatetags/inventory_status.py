from django import template

from apps.inventory.models import ItemStatus

register = template.Library()

_STATUS_BADGE_CLASSES = {
    ItemStatus.ACTIVE: "bg-green-950 text-green-400",
    ItemStatus.MAINTENANCE: "bg-amber-950 text-amber-400",
    ItemStatus.MISSING: "bg-red-950 text-red-400",
}
_DEFAULT_BADGE_CLASSES = "bg-zinc-800 text-zinc-400"


@register.filter
def status_badge_class(status: str) -> str:
    """Mapeia um valor de ItemStatus para as classes Tailwind do badge correspondente."""
    return _STATUS_BADGE_CLASSES.get(status, _DEFAULT_BADGE_CLASSES)
