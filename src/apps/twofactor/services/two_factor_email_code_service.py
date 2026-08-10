import secrets
from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from apps.settings.services.email_configuration_resolver_service import (
    EmailConfigurationResolverService,
)
from apps.twofactor.models import TwoFactorDevice, TwoFactorEmailCode

SUBJECT_TEMPLATE = "twofactor/emails/two_factor_code_subject.txt"
BODY_TEMPLATE = "twofactor/emails/two_factor_code_body.txt"

_DUMMY_HASH = make_password("__dummy__")


class TwoFactorEmailCodeService:
    """Gera, envia e valida o código de 6 dígitos por e-mail — mesma lógica de
    apps.security.services.PasswordResetOTPService (hash, expiração, tentativas
    limitadas), só que o canal de entrega é o dispositivo 2FA em vez do fluxo de
    recuperação de senha."""

    CODE_LENGTH = 6
    EXPIRATION_MINUTES = 10
    MAX_ATTEMPTS = 5

    @staticmethod
    def send(device: TwoFactorDevice) -> None:
        code = f"{secrets.randbelow(10 ** TwoFactorEmailCodeService.CODE_LENGTH):0{TwoFactorEmailCodeService.CODE_LENGTH}d}"

        # Invalida códigos anteriores ainda não usados — só o mais recente enviado
        # deve ser aceito, evita que um código antigo esquecido na caixa de entrada
        # continue funcionando depois de um reenvio.
        device.email_codes.filter(consumed_at__isnull=True).update(consumed_at=timezone.now())

        TwoFactorEmailCode.objects.create(
            device=device,
            code_hash=make_password(code),
            expires_at=timezone.now() + timedelta(minutes=TwoFactorEmailCodeService.EXPIRATION_MINUTES),
        )

        context = {"code": code, "expiration_minutes": TwoFactorEmailCodeService.EXPIRATION_MINUTES}
        subject = render_to_string(SUBJECT_TEMPLATE, context).strip()
        body = render_to_string(BODY_TEMPLATE, context)
        from_email = EmailConfigurationResolverService().resolve().default_from_email

        send_mail(subject, body, from_email, [device.user.email])

    @staticmethod
    def verify(device: TwoFactorDevice, raw_code: str) -> bool:
        code_entry = device.email_codes.filter(consumed_at__isnull=True).order_by("-created_at").first()

        if not code_entry:
            check_password(raw_code or "", _DUMMY_HASH)  # tempo constante
            return False

        if code_entry.expires_at < timezone.now():
            code_entry.consumed_at = timezone.now()
            code_entry.save(update_fields=["consumed_at"])
            return False

        if code_entry.attempts >= TwoFactorEmailCodeService.MAX_ATTEMPTS:
            return False

        if not check_password(raw_code or "", code_entry.code_hash):
            code_entry.attempts += 1
            code_entry.save(update_fields=["attempts"])
            return False

        code_entry.consumed_at = timezone.now()
        code_entry.save(update_fields=["consumed_at"])
        return True

    @staticmethod
    def mask_email(email: str) -> str:
        local, _, domain = email.partition("@")
        if not domain:
            return email
        visible = local[:2]
        return f"{visible}{'*' * max(len(local) - len(visible), 3)}@{domain}"
