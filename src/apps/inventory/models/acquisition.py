from django.db import models

from apps.common.models import BaseModelAbstract

from .item import Item
from .supplier import Supplier


class Acquisition(BaseModelAbstract):
    item = models.OneToOneField(
        Item,
        on_delete=models.CASCADE,
        related_name="acquisition",
        verbose_name="Item",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acquisitions",
        verbose_name="Fornecedor",
    )
    invoice_number = models.CharField(max_length=50, blank=True, verbose_name="Número da NF")
    purchase_date = models.DateField(null=True, blank=True, verbose_name="Data da compra")
    value = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Valor de aquisição"
    )
    warranty_months = models.PositiveIntegerField(null=True, blank=True, verbose_name="Garantia (meses)")
    warranty_expiry = models.DateField(null=True, blank=True, verbose_name="Vencimento da garantia")

    class Meta:
        verbose_name = "Aquisição"
        verbose_name_plural = "Aquisições"

    def __str__(self):
        return f"Aquisição de {self.item}"
