from django.conf import settings
from django.db import models

from apps.common.models import BaseModelAbstract

from .item import Item
from .sector import Location, Sector


class Movement(BaseModelAbstract):
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name="movements",
        verbose_name="Item",
    )
    from_sector = models.ForeignKey(
        Sector,
        on_delete=models.PROTECT,
        related_name="outgoing_movements",
        verbose_name="Setor de origem",
    )
    to_sector = models.ForeignKey(
        Sector,
        on_delete=models.PROTECT,
        related_name="incoming_movements",
        verbose_name="Setor de destino",
    )
    from_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outgoing_movements",
        verbose_name="Localização de origem",
    )
    to_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incoming_movements",
        verbose_name="Localização de destino",
    )
    moved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="movements_registered",
        verbose_name="Registrado por",
    )
    moved_at = models.DateTimeField(verbose_name="Data/hora da movimentação")
    reason = models.TextField(blank=True, verbose_name="Motivo")

    class Meta:
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"
        ordering = ["-moved_at"]

    def __str__(self):
        return f"{self.item} | {self.from_sector} → {self.to_sector}"
