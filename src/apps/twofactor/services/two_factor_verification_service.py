import re

from django.contrib.auth.hashers import check_password
from django.utils import timezone

from apps.twofactor.models import TwoFactorDevice
from apps.twofactor.services.two_factor_email_code_service import TwoFactorEmailCodeService

_NON_ALNUM = re.compile(r"[^A-Z0-9]")


class TwoFactorVerificationService:
    """Valida um código digitado contra o dispositivo confirmado de um usuário —
    tenta como código enviado por e-mail primeiro e, se não bater, como código de
    recuperação (consumindo-o no processo, já que é de uso único)."""

    @staticmethod
    def verify(device: TwoFactorDevice, raw_code: str) -> bool:
        code = (raw_code or "").strip()
        if not code:
            return False

        if TwoFactorEmailCodeService.verify(device, code):
            return True

        return TwoFactorVerificationService._consume_recovery_code(device, code)

    @staticmethod
    def _consume_recovery_code(device: TwoFactorDevice, raw_code: str) -> bool:
        normalized = _NON_ALNUM.sub("", raw_code.upper())

        for recovery_code in device.recovery_codes.filter(used_at__isnull=True):
            if check_password(normalized, recovery_code.code_hash):
                recovery_code.used_at = timezone.now()
                recovery_code.save(update_fields=["used_at"])
                return True

        return False
