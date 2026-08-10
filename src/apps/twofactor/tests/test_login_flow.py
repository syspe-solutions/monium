from django.core import mail
from django.test import TestCase
from django.urls import reverse

from apps.account.models import User
from apps.organizations.models import Membership, MembershipRole, Organization
from apps.twofactor.services import (
    TwoFactorActivationService,
    TwoFactorLoginChallengeService,
    TwoFactorSetupService,
)

from .test_services import configure_email_settings, latest_sent_code


def give_organization(user):
    organization = Organization.objects.create(
        name=user.username, slug=f"org-{user.username}",
        industry="technology", size="1-10", primary_goal="it_equipment",
    )
    Membership.objects.create(organization=organization, user=user, role=MembershipRole.OWNER)
    return organization


class LoginWithoutTwoFactorTests(TestCase):
    def test_login_without_2fa_authenticates_immediately(self):
        user = User.objects.create_user(username="no2fa", password="12345", email="no2fa@example.com")
        give_organization(user)

        response = self.client.post(reverse("account:login"), {"username": "no2fa", "password": "12345"})

        self.assertRedirects(response, reverse("inventory:home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class LoginWithTwoFactorTests(TestCase):
    def setUp(self):
        configure_email_settings()
        self.user = User.objects.create_user(username="has2fa", password="12345", email="has2fa@example.com")
        give_organization(self.user)
        TwoFactorSetupService.start(self.user)
        self.recovery_codes = TwoFactorActivationService.activate(self.user, latest_sent_code())
        mail.outbox.clear()

    def _login_with_password(self):
        return self.client.post(reverse("account:login"), {"username": "has2fa", "password": "12345"})

    def test_correct_password_redirects_to_verify_without_authenticating(self):
        response = self._login_with_password()

        self.assertRedirects(response, reverse("twofactor:login_verify"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_verify_get_without_pending_challenge_redirects_to_login(self):
        response = self.client.get(reverse("twofactor:login_verify"))
        self.assertRedirects(response, reverse("account:login"))

    def test_verify_get_sends_a_code_by_email(self):
        self._login_with_password()

        response = self.client.get(reverse("twofactor:login_verify"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

    def test_verify_get_does_not_resend_on_a_second_visit(self):
        self._login_with_password()
        self.client.get(reverse("twofactor:login_verify"))
        self.client.get(reverse("twofactor:login_verify"))

        self.assertEqual(len(mail.outbox), 1)

    def test_verify_with_correct_emailed_code_completes_login(self):
        self._login_with_password()
        self.client.get(reverse("twofactor:login_verify"))
        code = latest_sent_code()

        response = self.client.post(reverse("twofactor:login_verify"), {"code": code})

        self.assertRedirects(response, reverse("inventory:home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user, self.user)

    def test_verify_with_recovery_code_completes_login(self):
        self._login_with_password()
        self.client.get(reverse("twofactor:login_verify"))

        response = self.client.post(reverse("twofactor:login_verify"), {"code": self.recovery_codes[0]})

        self.assertRedirects(response, reverse("inventory:home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_verify_with_wrong_code_does_not_authenticate(self):
        self._login_with_password()
        self.client.get(reverse("twofactor:login_verify"))

        response = self.client.post(reverse("twofactor:login_verify"), {"code": "000000"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "twofactor/login_verify.html")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_resend_sends_another_code_after_cooldown_bypass(self):
        self._login_with_password()
        self.client.get(reverse("twofactor:login_verify"))

        session = self.client.session
        session[TwoFactorLoginChallengeService.SESSION_LAST_SENT_AT_KEY] -= 60
        session.save()

        self.client.post(reverse("twofactor:login_verify"), {"action": "resend"})

        self.assertEqual(len(mail.outbox), 2)

    def test_resend_respects_cooldown(self):
        self._login_with_password()
        self.client.get(reverse("twofactor:login_verify"))

        self.client.post(reverse("twofactor:login_verify"), {"action": "resend"})

        self.assertEqual(len(mail.outbox), 1)

    def test_too_many_failed_attempts_forces_login_again(self):
        self._login_with_password()
        self.client.get(reverse("twofactor:login_verify"))

        for _ in range(TwoFactorLoginChallengeService.MAX_ATTEMPTS):
            response = self.client.post(reverse("twofactor:login_verify"), {"code": "000000"})

        self.assertRedirects(response, reverse("account:login"))
        self.assertIsNone(TwoFactorLoginChallengeService.get_pending_user(response.wsgi_request))

    def test_next_url_is_preserved_across_the_challenge(self):
        target = reverse("account:settings")
        self.client.post(reverse("account:login"), {
            "username": "has2fa", "password": "12345", "next": target,
        })
        self.client.get(reverse("twofactor:login_verify"))
        code = latest_sent_code()

        response = self.client.post(reverse("twofactor:login_verify"), {"code": code})

        self.assertRedirects(response, target)
