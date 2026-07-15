from django.conf import settings
from django.db import models

from apps.common.models import BaseModelAbstract


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Ativa"
    PAST_DUE = "past_due", "Pagamento pendente"
    CANCELED = "canceled", "Cancelada"


class Subscription(BaseModelAbstract):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription",
        verbose_name="Usuário",
    )
    plan_id = models.CharField(max_length=30, default="free", verbose_name="Plano")
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
        verbose_name="Status",
    )
    current_period_end = models.DateTimeField(null=True, blank=True, verbose_name="Fim do período atual")
    mp_preapproval_id = models.CharField(max_length=100, blank=True, verbose_name="ID da assinatura no Mercado Pago")

    class Meta:
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"

    def __str__(self):
        return f"{self.user} — {self.plan_id} ({self.status})"
