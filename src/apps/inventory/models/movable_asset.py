from django.db import models

from apps.common.models import BaseModelAbstract

from .category import Category
from .item import Item
from .sector import Location, Sector


class AssetStatus(models.TextChoices):
    IN_USE = "em_uso", "Em uso"
    STORED = "guardado", "Guardado"
    MAINTENANCE = "em_manutencao", "Em manutenção"
    DISCARDED = "descartado", "Descartado"
    MISSING = "extraviado", "Extraviado"


class MovableAsset(Item):
    """Bem móvel: mobiliário, equipamentos e demais itens patrimoniais rastreados por setor/localização."""

    item_ptr = models.OneToOneField(
        Item,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name="movable_asset",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="items",
        verbose_name="Categoria",
    )
    sector = models.ForeignKey(
        Sector,
        on_delete=models.PROTECT,
        related_name="items",
        verbose_name="Setor",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
        verbose_name="Localização",
    )
    status = models.CharField(
        max_length=20,
        choices=AssetStatus.choices,
        default=AssetStatus.IN_USE,
        verbose_name="Situação Patrimonial",
    )

    class Meta:
        verbose_name = "Bem Móvel"
        verbose_name_plural = "Bens Móveis"
        ordering = ["name"]

    def __str__(self):
        return f"[{self.code}] {self.name}"


class AssetSpec(BaseModelAbstract):
    asset = models.OneToOneField(
        MovableAsset,
        on_delete=models.CASCADE,
        related_name="spec",
        verbose_name="Bem Móvel",
    )
    brand = models.ForeignKey(
        "Brand",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="item_specs",
        verbose_name="Marca",
    )
    model_name = models.CharField(max_length=150, blank=True, verbose_name="Modelo")
    serial_number = models.CharField(max_length=150, blank=True, verbose_name="Número de série")
    image = models.ImageField(upload_to="inventory/items/", null=True, blank=True, verbose_name="Imagem")
    extra_attributes = models.JSONField(default=dict, blank=True, verbose_name="Atributos extras")

    class Meta:
        verbose_name = "Especificação do Bem Móvel"
        verbose_name_plural = "Especificações dos Bens Móveis"

    def __str__(self):
        return f"Spec — {self.asset}"
