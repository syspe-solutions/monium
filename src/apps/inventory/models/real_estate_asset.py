from django.db import models

from .item import Item
from .real_estate_category import RealEstateCategory


class CartorioSituacao(models.TextChoices):
    REGISTERED = "registrado", "Registrado"
    UNREGISTERED = "nao_registrado", "Não registrado"
    IN_PROGRESS = "em_registro", "Em processo de registro"


class ZonaTipo(models.TextChoices):
    URBANA = "urbana", "Urbana"
    RURAL = "rural", "Rural"


class RealEstateAsset(Item):
    """Bem imóvel: casas, apartamentos, terrenos e demais propriedades da organização."""

    item_ptr = models.OneToOneField(
        Item,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name="real_estate_asset",
    )

    category = models.ForeignKey(
        RealEstateCategory,
        on_delete=models.PROTECT,
        related_name="real_estate_assets",
        verbose_name="Categoria",
    )
    cartorio_situacao = models.CharField(
        max_length=20,
        choices=CartorioSituacao.choices,
        default=CartorioSituacao.UNREGISTERED,
        verbose_name="Situação em Cartório",
    )
    cep = models.CharField(max_length=9, blank=True, verbose_name="CEP")
    address = models.CharField(max_length=255, blank=True, verbose_name="Endereço")
    zone = models.CharField(
        max_length=10,
        choices=ZonaTipo.choices,
        blank=True,
        verbose_name="Zona",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Longitude")
    total_area = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Área total (m²)"
    )
    built_area = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Área construída (m²)"
    )

    class Meta:
        verbose_name = "Bem Imóvel"
        verbose_name_plural = "Bens Imóveis"
        ordering = ["name"]

    def __str__(self):
        return f"[{self.code}] {self.name}"
