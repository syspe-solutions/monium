from django.core import mail
from django.test import TestCase
from django.urls import reverse

from apps.account.models import User
from apps.organizations.models import Membership, MembershipRole, Organization
from apps.settings.models import EmailSettings
from apps.twofactor.models import TwoFactorDevice
from apps.twofactor.services import TwoFactorActivationService, TwoFactorSetupService

from .test_services import configure_email_settings, latest_sent_code


def give_organization(user):
    """RequireOrganizationMiddleware bloqueia usuários autenticados sem
    organização — mesmo helper usado em apps.account.tests.test_views."""
    organization = Organization.objects.create(
        name=user.username, slug=f"org-{user.username}",
        industry="technology", size="1-10", primary_goal="it_equipment",
    )
    Membership.objects.create(organization=organization, user=user, role=MembershipRole.OWNER)
    return organization


class TwoFactorSetupViewTests(TestCase):
    def setUp(self):
        configure_email_settings()
        self.user = User.objects.create_user(
            username="viewsetup", password="12345", email="viewsetup@example.com"
        )
        give_organization(self.user)
        self.client.force_login(self.user)

    def test_requires_authentication(self):
        self.client.logout()
        response = self.client.get(reverse("twofactor:setup"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account:login"), response.url)

    def test_get_sends_a_code_and_renders_the_masked_email(self):
        response = self.client.get(reverse("twofactor:setup"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "twofactor/setup.html")
        self.assertEqual(len(mail.outbox), 1)
        self.assertContains(response, response.context["setup"].masked_email)

    def test_get_does_not_resend_on_a_second_visit(self):
        self.client.get(reverse("twofactor:setup"))
        self.client.get(reverse("twofactor:setup"))

        self.assertEqual(len(mail.outbox), 1)

    def test_get_redirects_to_settings_when_email_is_not_configured(self):
        email_settings = EmailSettings.load()
        email_settings.is_enabled = False
        email_settings.save()

        response = self.client.get(reverse("twofactor:setup"))

        self.assertRedirects(response, reverse("account:settings"))
        self.assertFalse(TwoFactorDevice.objects.filter(user=self.user).exists())

    def test_get_redirects_to_settings_if_already_enabled(self):
        TwoFactorSetupService.start(self.user)
        TwoFactorActivationService.activate(self.user, latest_sent_code())

        response = self.client.get(reverse("twofactor:setup"))

        self.assertRedirects(response, reverse("account:settings"))

    def test_resend_sends_another_code(self):
        self.client.get(reverse("twofactor:setup"))

        response = self.client.post(reverse("twofactor:setup"), {"action": "resend"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 2)

    def test_post_with_valid_code_enables_2fa_and_shows_recovery_codes(self):
        self.client.get(reverse("twofactor:setup"))
        code = latest_sent_code()

        response = self.client.post(reverse("twofactor:setup"), {"code": code})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "twofactor/recovery_codes.html")
        self.assertEqual(len(response.context["recovery_codes"]), 8)

        device = TwoFactorDevice.objects.get(user=self.user)
        self.assertTrue(device.confirmed)

    def test_post_with_invalid_code_shows_error_and_keeps_device_unconfirmed(self):
        self.client.get(reverse("twofactor:setup"))

        response = self.client.post(reverse("twofactor:setup"), {"code": "000000"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "twofactor/setup.html")
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(TwoFactorDevice.objects.get(user=self.user).confirmed)


class TwoFactorDisableViewTests(TestCase):
    def setUp(self):
        configure_email_settings()
        self.user = User.objects.create_user(
            username="viewdisable", password="12345", email="viewdisable@example.com"
        )
        give_organization(self.user)
        self.client.force_login(self.user)
        TwoFactorSetupService.start(self.user)
        TwoFactorActivationService.activate(self.user, latest_sent_code())

    def test_post_disables_two_factor(self):
        response = self.client.post(reverse("twofactor:disable"))

        self.assertRedirects(response, reverse("account:settings"))
        self.assertFalse(TwoFactorDevice.objects.filter(user=self.user).exists())

    def test_requires_authentication(self):
        self.client.logout()
        response = self.client.post(reverse("twofactor:disable"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account:login"), response.url)
