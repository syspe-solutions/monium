from django.db import models

from apps.common.models import BaseModelAbstract

from .two_factor_device import TwoFactorDevice


class TwoFactorRecoveryCode(BaseModelAbstract):
    """Código de uso único para entrar quando o autenticador TOTP não está
    disponível (celular perdido/trocado). Armazenado com hash, nunca em texto
    puro — o texto puro só existe no momento da geração, mostrado uma vez."""

    device = models.ForeignKey(
        TwoFactorDevice,
        on_delete=models.CASCADE,
        related_name="recovery_codes",
        verbose_name="Dispositivo",
    )
    code_hash = models.CharField(max_length=128, verbose_name="Hash do código")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="Usado em")

    class Meta:
        verbose_name = "Código de recuperação"
        verbose_name_plural = "Códigos de recuperação"

    def __str__(self):
        return f"Código de recuperação de {self.device.user} ({'usado' if self.used_at else 'disponível'})"
