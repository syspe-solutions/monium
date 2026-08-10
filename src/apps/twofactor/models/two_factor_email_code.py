from django.db import models

from apps.common.models import BaseModelAbstract

from .two_factor_device import TwoFactorDevice


class TwoFactorEmailCode(BaseModelAbstract):
    """Código de 6 dígitos enviado por e-mail para confirmar a configuração do
    2FA ou para validar um login — nunca armazenado em texto puro, só o hash
    (mesmo padrão de apps.security.models.PasswordResetOTP)."""

    device = models.ForeignKey(
        TwoFactorDevice,
        on_delete=models.CASCADE,
        related_name="email_codes",
        verbose_name="Dispositivo",
    )
    code_hash = models.CharField(max_length=128, verbose_name="Hash do código")
    expires_at = models.DateTimeField(verbose_name="Expira em")
    attempts = models.PositiveSmallIntegerField(default=0, verbose_name="Tentativas")
    consumed_at = models.DateTimeField(null=True, blank=True, verbose_name="Consumido em")

    class Meta:
        verbose_name = "Código de verificação por e-mail"
        verbose_name_plural = "Códigos de verificação por e-mail"

    def __str__(self):
        return f"Código 2FA de {self.device.user} ({'usado' if self.consumed_at else 'ativo'})"
