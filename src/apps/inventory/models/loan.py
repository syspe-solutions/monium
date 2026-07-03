from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModelAbstract

from .item import Item


class LoanStatus(models.TextChoices):
    ACTIVE = "ativo", "Ativo"
    RETURNED = "devolvido", "Devolvido"
    OVERDUE = "atrasado", "Atrasado"


class Loan(BaseModelAbstract):
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name="loans",
        verbose_name="Item",
    )
    loaned_to = models.CharField(max_length=255, verbose_name="Emprestado para")
    loaned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="loans_registered",
        verbose_name="Registrado por",
    )
    loaned_at = models.DateTimeField(verbose_name="Data/hora do empréstimo")
    expected_return = models.DateField(verbose_name="Previsão de retorno")
    returned_at = models.DateTimeField(null=True, blank=True, verbose_name="Data/hora de devolução")
    status = models.CharField(
        max_length=20,
        choices=LoanStatus.choices,
        default=LoanStatus.ACTIVE,
        verbose_name="Status",
    )

    class Meta:
        verbose_name = "Empréstimo"
        verbose_name_plural = "Empréstimos"
        ordering = ["-loaned_at"]

    def __str__(self):
        return f"{self.item} → {self.loaned_to}"

    @property
    def is_overdue(self):
        return self.status == LoanStatus.ACTIVE and self.expected_return < timezone.now().date()
