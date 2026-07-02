from django.db import models

from apps.common.models import BaseModelAbstract

from .item import Item


class Attachment(BaseModelAbstract):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Item",
    )
    label = models.CharField(max_length=150, verbose_name="Rótulo")
    file = models.ForeignKey(
        "common.StoredFile",
        on_delete=models.PROTECT,
        related_name="inventory_attachments",
        verbose_name="Arquivo",
    )

    class Meta:
        verbose_name = "Anexo"
        verbose_name_plural = "Anexos"

    def __str__(self):
        return f"{self.label} — {self.item}"
