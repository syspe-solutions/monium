from django.conf import settings
from django.db import models

from apps.common.models import BaseModelAbstract


class TwoFactorDevice(BaseModelAbstract):
    """Marca se um usuário tem autenticação em duas etapas por e-mail habilitada.
    Enquanto `confirmed` for False, está pendente de ativação — um código já pode
    ter sido enviado para o e-mail cadastrado do usuário, mas nenhum código foi
    validado ainda, então não conta como 2FA habilitado."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="two_factor_device",
        verbose_name="Usuário",
    )
    confirmed = models.BooleanField(default=False, verbose_name="Confirmado")
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name="Confirmado em")

    class Meta:
        verbose_name = "Dispositivo de autenticação em duas etapas"
        verbose_name_plural = "Dispositivos de autenticação em duas etapas"

    def __str__(self):
        return f"2FA de {self.user} ({'confirmado' if self.confirmed else 'pendente'})"
