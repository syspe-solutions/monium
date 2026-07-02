from django.db import models

from apps.common.models import BaseModelAbstract

from .item import Item


class MaintenanceStatus(models.TextChoices):
    OPEN = "aberta", "Aberta"
    IN_PROGRESS = "em_andamento", "Em andamento"
    DONE = "concluida", "Concluída"
    CANCELLED = "cancelada", "Cancelada"


class Maintenance(BaseModelAbstract):
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name="maintenances",
        verbose_name="Item",
    )
    description = models.TextField(verbose_name="Descrição")
    status = models.CharField(
        max_length=20,
        choices=MaintenanceStatus.choices,
        default=MaintenanceStatus.OPEN,
        verbose_name="Status",
    )
    started_at = models.DateField(verbose_name="Data de início")
    finished_at = models.DateField(null=True, blank=True, verbose_name="Data de conclusão")
    cost = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Custo"
    )
    performed_by = models.CharField(max_length=255, blank=True, verbose_name="Executado por")
    result = models.TextField(blank=True, verbose_name="Resultado")

    class Meta:
        verbose_name = "Manutenção"
        verbose_name_plural = "Manutenções"
        ordering = ["-started_at"]

    def __str__(self):
        return f"Manutenção de {self.item} ({self.started_at})"
