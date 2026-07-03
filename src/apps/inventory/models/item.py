from django.db import models

from apps.common.models import BaseModelAbstract

from .category import Category
from .sector import Location, Sector


class ItemStatus(models.TextChoices):
    ACTIVE = "ativo", "Ativo"
    MAINTENANCE = "em_manutencao", "Em manutenção"
    WRITTEN_OFF = "baixado", "Baixado"
    MISSING = "extraviado", "Extraviado"


class ItemCondition(models.TextChoices):
    EXCELLENT = "otimo", "Ótimo"
    GOOD = "bom", "Bom"
    FAIR = "regular", "Regular"
    POOR = "ruim", "Ruim"


class Item(BaseModelAbstract):
    # Identidade
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Organização",
    )
    code = models.CharField(max_length=50, verbose_name="Código / Patrimônio")
    name = models.CharField(max_length=255, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="items",
        verbose_name="Categoria",
    )
    # Localização operacional
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
    responsible = models.CharField(max_length=255, blank=True, verbose_name="Responsável")
    # Estado
    status = models.CharField(
        max_length=20,
        choices=ItemStatus.choices,
        default=ItemStatus.ACTIVE,
        verbose_name="Status",
    )
    condition = models.CharField(
        max_length=20,
        choices=ItemCondition.choices,
        default=ItemCondition.GOOD,
        verbose_name="Condição",
    )
    notes = models.TextField(blank=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Itens"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "code"], name="unique_item_code_per_organization"),
        ]

    def __str__(self):
        return f"[{self.code}] {self.name}"


class ItemSpec(BaseModelAbstract):
    item = models.OneToOneField(
        Item,
        on_delete=models.CASCADE,
        related_name="spec",
        verbose_name="Item",
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
        verbose_name = "Especificação do Item"
        verbose_name_plural = "Especificações dos Itens"

    def __str__(self):
        return f"Spec — {self.item}"
