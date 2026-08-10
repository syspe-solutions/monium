from datetime import timedelta

from django.utils import timezone

from apps.inventory.models import Acquisition

DEFAULT_WARNING_WINDOW_DAYS = 30


def get_expiring_warranties(organization=None, within_days: int = DEFAULT_WARNING_WINDOW_DAYS):
    """Aquisições com garantia vencendo entre hoje e `within_days` dias à
    frente — já vencidas não entram aqui, viram histórico e não alerta mais
    (evita ficar avisando pra sempre sobre algo que já passou)."""
    today = timezone.now().date()
    queryset = Acquisition.objects.filter(
        warranty_expiry__gte=today,
        warranty_expiry__lte=today + timedelta(days=within_days),
    ).select_related("item")

    if organization is not None:
        queryset = queryset.filter(item__organization=organization)

    return queryset.order_by("warranty_expiry")
