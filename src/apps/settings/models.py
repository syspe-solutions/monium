import uuid

from django.db import models

from apps.common.models import BaseModelAbstract
from apps.settings.fields import EncryptedCharField


class EmailSettings(BaseModelAbstract):
    """Configuração SMTP editável pela interface. Modelo singleton: sempre existe
    no máximo uma linha, identificada por SINGLETON_ID. Não há fallback para
    variáveis de ambiente — quando desabilitada ou sem host definido, o envio de
    e-mails fica bloqueado até a configuração ser concluída por aqui."""

    SINGLETON_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

    is_enabled = models.BooleanField(
        default=False,
        verbose_name="Ativar servidor SMTP",
        help_text="Enquanto desativado, o envio de e-mails do sistema fica bloqueado.",
    )
    host = models.CharField(max_length=255, blank=True, verbose_name="Servidor SMTP")
    port = models.PositiveIntegerField(default=587, verbose_name="Porta")
    use_tls = models.BooleanField(default=True, verbose_name="Usar TLS")
    use_ssl = models.BooleanField(default=False, verbose_name="Usar SSL")
    host_user = models.CharField(max_length=255, blank=True, verbose_name="Usuário SMTP")
    host_password = EncryptedCharField(max_length=255, blank=True, verbose_name="Senha SMTP")
    default_from_email = models.EmailField(blank=True, verbose_name="E-mail remetente padrão")

    class Meta:
        verbose_name = "Configuração de E-mail"
        verbose_name_plural = "Configurações de E-mail"

    def __str__(self):
        return "Configuração de E-mail"

    def save(self, *args, **kwargs):
        self.id = self.SINGLETON_ID
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise NotImplementedError("EmailSettings é um singleton e não pode ser excluído.")

    @classmethod
    def load(cls):
        instance, _created = cls.objects.get_or_create(id=cls.SINGLETON_ID)
        return instance
