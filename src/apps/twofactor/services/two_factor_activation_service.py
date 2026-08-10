import secrets

from django.contrib.auth.hashers import make_password
from django.utils import timezone

from apps.twofactor.models import TwoFactorDevice, TwoFactorRecoveryCode
from apps.twofactor.services.two_factor_email_code_service import TwoFactorEmailCodeService

RECOVERY_CODE_COUNT = 8


class TwoFactorActivationError(Exception):
    pass


class TwoFactorActivationService:
    """Confirma o dispositivo pendente de um usuário com o código enviado por
    e-mail, e emite os códigos de recuperação — só nesse momento, porque é a
    única vez em que eles existem em texto puro."""

    @staticmethod
    def activate(user, code: str) -> list[str]:
        try:
            device = TwoFactorDevice.objects.get(user=user, confirmed=False)
        except TwoFactorDevice.DoesNotExist:
            raise TwoFactorActivationError("Nenhuma configuração de 2FA pendente para este usuário.")

        if not TwoFactorEmailCodeService.verify(device, code):
            raise TwoFactorActivationError("Código inválido ou expirado.")

        device.confirmed = True
        device.confirmed_at = timezone.now()
        device.save(update_fields=["confirmed", "confirmed_at"])

        return TwoFactorActivationService._issue_recovery_codes(device)

    @staticmethod
    def _issue_recovery_codes(device: TwoFactorDevice) -> list[str]:
        device.recovery_codes.all().delete()

        # O hash guarda a forma normalizada (sem hífen) — o hífen no texto
        # mostrado ao usuário é só formatação, não faz parte do código.
        raw_codes = [secrets.token_hex(4).upper() for _ in range(RECOVERY_CODE_COUNT)]
        TwoFactorRecoveryCode.objects.bulk_create([
            TwoFactorRecoveryCode(device=device, code_hash=make_password(raw))
            for raw in raw_codes
        ])
        return [f"{raw[:4]}-{raw[4:]}" for raw in raw_codes]
