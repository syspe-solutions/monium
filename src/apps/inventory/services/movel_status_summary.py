from apps.inventory.models import Movel, MovelStatus


def get_movel_status_summary(organization) -> dict:
    """Conta os bens móveis da organização por status.

    Usado tanto pelo Home quanto pela visão de categorias — antes cada view
    repetia a mesma sequência de queries de forma independente.
    """
    items = Movel.objects.filter(organization=organization)
    return {
        "total_items": items.count(),
        "active_items": items.filter(status=MovelStatus.IN_USE).count(),
        "maintenance_items": items.filter(status=MovelStatus.MAINTENANCE).count(),
        "missing_items": items.filter(status=MovelStatus.MISSING).count(),
        "written_off_items": items.filter(status=MovelStatus.DISCARDED).count(),
    }
