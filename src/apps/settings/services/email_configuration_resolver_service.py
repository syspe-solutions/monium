from apps.settings.dtos.email_configuration_dto import EmailConfigurationDTO
from apps.settings.exceptions import EmailNotConfiguredError
from apps.settings.models import EmailSettings


class EmailConfigurationResolverService:
    """Resolve a configuração SMTP cadastrada em Configurações > E-mail. Não há
    fallback para variáveis de ambiente: o envio de e-mail depende exclusivamente
    do cadastro feito pela interface, com um servidor ativado e host preenchido."""

    def resolve(self) -> EmailConfigurationDTO:
        email_settings = EmailSettings.load()
        if not email_settings.is_enabled or not email_settings.host:
            raise EmailNotConfiguredError(
                "SMTP não configurado. Cadastre e ative o servidor de e-mail em "
                "Configurações > E-mail."
            )
        return EmailConfigurationDTO(
            host=email_settings.host,
            port=email_settings.port,
            use_tls=email_settings.use_tls,
            use_ssl=email_settings.use_ssl,
            username=email_settings.host_user,
            password=email_settings.host_password,
            default_from_email=email_settings.default_from_email,
        )
