from apps.inventory.models import AssetStatus, MovableAsset


def get_asset_status_summary(organization) -> dict:
    """Conta os bens móveis da organização por status.

    Usado tanto pelo Home quanto pela visão de categorias — antes cada view
    repetia a mesma sequência de queries de forma independente.
    """
    items = MovableAsset.objects.filter(organization=organization)
    return {
        "total_items": items.count(),
        "active_items": items.filter(status=AssetStatus.IN_USE).count(),
        "maintenance_items": items.filter(status=AssetStatus.MAINTENANCE).count(),
        "missing_items": items.filter(status=AssetStatus.MISSING).count(),
        "written_off_items": items.filter(status=AssetStatus.DISCARDED).count(),
    }
