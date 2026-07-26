from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend

from apps.settings.services.email_configuration_resolver_service import (
    EmailConfigurationResolverService,
)


class DynamicSMTPEmailBackend(SMTPEmailBackend):
    """Backend de e-mail que resolve host/porta/credenciais em tempo de envio, a
    partir da configuração cadastrada em Configurações > E-mail. Se não houver
    servidor ativado, EmailConfigurationResolverService.resolve() levanta
    EmailNotConfiguredError e o envio falha explicitamente."""

    def __init__(self, *args, **kwargs):
        configuration = EmailConfigurationResolverService().resolve()
        kwargs.setdefault("host", configuration.host)
        kwargs.setdefault("port", configuration.port)
        kwargs.setdefault("username", configuration.username)
        kwargs.setdefault("password", configuration.password)
        kwargs.setdefault("use_tls", configuration.use_tls)
        kwargs.setdefault("use_ssl", configuration.use_ssl)
        super().__init__(*args, **kwargs)
