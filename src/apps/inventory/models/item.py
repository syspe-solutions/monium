from django.db import models

from apps.common.models import BaseModelAbstract


class ItemCondition(models.TextChoices):
    EXCELLENT = "otimo", "Ótimo"
    GOOD = "bom", "Bom"
    FAIR = "regular", "Regular"
    POOR = "ruim", "Ruim"


class AssetOwnership(models.TextChoices):
    OWN = "proprio", "Próprio"
    THIRD_PARTY = "terceiros", "Terceiros"


class Item(BaseModelAbstract):
    """Base comum a bens móveis (MovableAsset) e imóveis (RealEstateAsset)."""

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Organização",
    )
    code = models.CharField(max_length=50, verbose_name="Código / Patrimônio")
    name = models.CharField(max_length=255, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    responsible = models.CharField(max_length=255, blank=True, verbose_name="Responsável")
    ownership = models.CharField(
        max_length=20,
        choices=AssetOwnership.choices,
        default=AssetOwnership.OWN,
        verbose_name="Titularidade",
    )
    condition = models.CharField(
        max_length=20,
        choices=ItemCondition.choices,
        default=ItemCondition.GOOD,
        verbose_name="Condição",
    )
    notes = models.TextField(blank=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Bem"
        verbose_name_plural = "Bens"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "code"], name="unique_item_code_per_organization"),
        ]

    def __str__(self):
        return f"[{self.code}] {self.name}"
