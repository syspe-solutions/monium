from django.core import mail
from django.test import TestCase

from apps.account.models import User
from apps.settings.exceptions import EmailNotConfiguredError
from apps.settings.models import EmailSettings
from apps.twofactor.models import TwoFactorDevice, TwoFactorRecoveryCode
from apps.twofactor.services import (
    TwoFactorActivationError,
    TwoFactorActivationService,
    TwoFactorDisableService,
    TwoFactorEmailCodeService,
    TwoFactorSetupService,
    TwoFactorVerificationService,
)


def configure_email_settings():
    email_settings = EmailSettings.load()
    email_settings.is_enabled = True
    email_settings.host = "smtp.example.com"
    email_settings.default_from_email = "no-reply@example.com"
    email_settings.save()
    return email_settings


def latest_sent_code() -> str:
    """Extrai o código de 6 dígitos do corpo do último e-mail enviado nos
    testes — mail.outbox é preenchido pelo backend locmem que o test runner do
    Django ativa automaticamente."""
    body = mail.outbox[-1].body
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.isdigit() and len(stripped) == 6:
            return stripped
    raise AssertionError(f"Nenhum código de 6 dígitos encontrado no e-mail: {body!r}")


class TwoFactorSetupServiceTests(TestCase):
    def setUp(self):
        configure_email_settings()
        self.user = User.objects.create_user(
            username="setupuser", password="12345", email="setupuser@example.com"
        )

    def test_start_creates_a_pending_device_and_sends_a_code(self):
        setup = TwoFactorSetupService.start(self.user)

        device = TwoFactorDevice.objects.get(user=self.user)
        self.assertFalse(device.confirmed)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email.split("@")[0][:2], setup.masked_email)

    def test_start_does_not_resend_on_repeated_calls(self):
        TwoFactorSetupService.start(self.user)
        TwoFactorSetupService.start(self.user)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(TwoFactorDevice.objects.filter(user=self.user).count(), 1)

    def test_resend_always_sends_a_new_code(self):
        TwoFactorSetupService.start(self.user)
        TwoFactorSetupService.resend(self.user)

        self.assertEqual(len(mail.outbox), 2)

    def test_start_raises_when_email_is_not_configured(self):
        email_settings = EmailSettings.load()
        email_settings.is_enabled = False
        email_settings.save()

        other_user = User.objects.create_user(
            username="noemailconfig", password="12345", email="noemailconfig@example.com"
        )

        with self.assertRaises(EmailNotConfiguredError):
            TwoFactorSetupService.start(other_user)

        self.assertFalse(TwoFactorDevice.objects.filter(user=other_user).exists())

    def test_is_email_available_reflects_email_settings(self):
        self.assertTrue(TwoFactorSetupService.is_email_available())

        email_settings = EmailSettings.load()
        email_settings.is_enabled = False
        email_settings.save()

        self.assertFalse(TwoFactorSetupService.is_email_available())


class TwoFactorActivationServiceTests(TestCase):
    def setUp(self):
        configure_email_settings()
        self.user = User.objects.create_user(
            username="activateuser", password="12345", email="activateuser@example.com"
        )
        TwoFactorSetupService.start(self.user)
        self.code = latest_sent_code()

    def test_activate_with_valid_code_confirms_device_and_returns_recovery_codes(self):
        recovery_codes = TwoFactorActivationService.activate(self.user, self.code)

        device = TwoFactorDevice.objects.get(user=self.user)
        self.assertTrue(device.confirmed)
        self.assertIsNotNone(device.confirmed_at)
        self.assertEqual(len(recovery_codes), 8)
        self.assertEqual(TwoFactorRecoveryCode.objects.filter(device=device).count(), 8)

    def test_activate_with_invalid_code_raises_and_leaves_device_unconfirmed(self):
        with self.assertRaises(TwoFactorActivationError):
            TwoFactorActivationService.activate(self.user, "000000")

        device = TwoFactorDevice.objects.get(user=self.user)
        self.assertFalse(device.confirmed)

    def test_activate_without_pending_device_raises(self):
        other_user = User.objects.create_user(
            username="noactivation", password="12345", email="noactivation@example.com"
        )

        with self.assertRaises(TwoFactorActivationError):
            TwoFactorActivationService.activate(other_user, "123456")


class TwoFactorVerificationServiceTests(TestCase):
    def setUp(self):
        configure_email_settings()
        self.user = User.objects.create_user(
            username="verifyuser", password="12345", email="verifyuser@example.com"
        )
        TwoFactorSetupService.start(self.user)
        self.recovery_codes = TwoFactorActivationService.activate(self.user, latest_sent_code())
        self.device = TwoFactorDevice.objects.get(user=self.user)

    def test_verify_accepts_a_valid_emailed_code(self):
        TwoFactorEmailCodeService.send(self.device)
        code = latest_sent_code()

        self.assertTrue(TwoFactorVerificationService.verify(self.device, code))

    def test_verify_rejects_an_invalid_code(self):
        TwoFactorEmailCodeService.send(self.device)
        self.assertFalse(TwoFactorVerificationService.verify(self.device, "000000"))

    def test_verify_accepts_and_consumes_a_recovery_code(self):
        code = self.recovery_codes[0]

        self.assertTrue(TwoFactorVerificationService.verify(self.device, code))
        # Uso único: a segunda tentativa com o mesmo código falha.
        self.assertFalse(TwoFactorVerificationService.verify(self.device, code))

    def test_verify_accepts_recovery_code_without_the_dash(self):
        code = self.recovery_codes[1].replace("-", "").lower()
        self.assertTrue(TwoFactorVerificationService.verify(self.device, code))


class TwoFactorEmailCodeServiceTests(TestCase):
    def setUp(self):
        configure_email_settings()
        self.user = User.objects.create_user(
            username="emailcodeuser", password="12345", email="emailcodeuser@example.com"
        )
        self.device = TwoFactorDevice.objects.create(user=self.user)

    def test_sending_a_new_code_invalidates_the_previous_one(self):
        TwoFactorEmailCodeService.send(self.device)
        first_code = latest_sent_code()

        TwoFactorEmailCodeService.send(self.device)

        self.assertFalse(TwoFactorEmailCodeService.verify(self.device, first_code))

    def test_verify_fails_after_max_attempts(self):
        TwoFactorEmailCodeService.send(self.device)

        for _ in range(TwoFactorEmailCodeService.MAX_ATTEMPTS):
            TwoFactorEmailCodeService.verify(self.device, "000000")

        code = latest_sent_code()
        self.assertFalse(TwoFactorEmailCodeService.verify(self.device, code))

    def test_mask_email(self):
        self.assertEqual(TwoFactorEmailCodeService.mask_email("ab@example.com"), "ab***@example.com")
        self.assertEqual(TwoFactorEmailCodeService.mask_email("jonathas@example.com"), "jo******@example.com")


class TwoFactorDisableServiceTests(TestCase):
    def setUp(self):
        configure_email_settings()

    def test_disable_removes_the_device_and_its_recovery_codes(self):
        user = User.objects.create_user(username="disableuser", password="12345", email="disableuser@example.com")
        TwoFactorSetupService.start(user)
        TwoFactorActivationService.activate(user, latest_sent_code())

        disabled = TwoFactorDisableService.disable(user)

        self.assertTrue(disabled)
        self.assertFalse(TwoFactorDevice.objects.filter(user=user).exists())
        self.assertFalse(TwoFactorRecoveryCode.objects.exists())

    def test_disable_without_a_device_returns_false(self):
        user = User.objects.create_user(username="nodevice", password="12345", email="nodevice@example.com")
        self.assertFalse(TwoFactorDisableService.disable(user))
