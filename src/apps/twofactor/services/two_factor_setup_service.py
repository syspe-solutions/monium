from apps.settings.exceptions import EmailNotConfiguredError
from apps.settings.models import EmailSettings
from apps.twofactor.dtos import TwoFactorSetupDTO
from apps.twofactor.models import TwoFactorDevice
from apps.twofactor.services.two_factor_email_code_service import TwoFactorEmailCodeService

_NOT_CONFIGURED_MESSAGE = (
    "SMTP não configurado. Peça a um administrador para configurar o envio de "
    "e-mails em Configurações > E-mail."
)


class TwoFactorSetupService:
    """Prepara o dispositivo 2FA pendente de um usuário e dispara o código de
    confirmação por e-mail. Autenticação em duas etapas só pode ser ativada
    quando o servidor SMTP da instância está configurado — sem isso não há como
    entregar o código, então nem o dispositivo pendente é criado."""

    @staticmethod
    def is_email_available() -> bool:
        email_settings = EmailSettings.load()
        return bool(email_settings.is_enabled and email_settings.host)

    @staticmethod
    def start(user) -> TwoFactorSetupDTO:
        """Idempotente: só envia um código novo na primeira chamada (quando o
        dispositivo pendente ainda não existe). Reentrar aqui — ex.: usuário
        atualiza a página — não deve disparar um e-mail novo a cada vez; para
        isso existe TwoFactorSetupService.resend()."""
        TwoFactorSetupService._guard_email_available()

        device, created = TwoFactorDevice.objects.get_or_create(user=user)
        if created:
            TwoFactorEmailCodeService.send(device)

        return TwoFactorSetupDTO(masked_email=TwoFactorEmailCodeService.mask_email(user.email))

    @staticmethod
    def resend(user) -> TwoFactorSetupDTO:
        TwoFactorSetupService._guard_email_available()

        device, _created = TwoFactorDevice.objects.get_or_create(user=user)
        TwoFactorEmailCodeService.send(device)

        return TwoFactorSetupDTO(masked_email=TwoFactorEmailCodeService.mask_email(user.email))

    @staticmethod
    def _guard_email_available() -> None:
        if not TwoFactorSetupService.is_email_available():
            raise EmailNotConfiguredError(_NOT_CONFIGURED_MESSAGE)
