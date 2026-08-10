from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.organizations.models import Membership, MembershipRole, Organization
from apps.settings.models import EmailSettings

User = get_user_model()


def give_organization(user, name):
    organization = Organization.objects.create(name=name)
    Membership.objects.create(user=user, organization=organization, role=MembershipRole.OWNER)
    return organization


class SettingsViewTest(TestCase):
    def test_settings_page_renders_for_logged_in_user(self):
        user = User.objects.create_user(username="settingsuser", password="x", email="s@s.com")
        give_organization(user, "Test Org")
        self.client.force_login(user)
        response = self.client.get(reverse("account:settings"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Language")
        self.assertContains(response, "Help & Support")

    def test_settings_page_requires_login(self):
        response = self.client.get(reverse("account:settings"))
        self.assertNotEqual(response.status_code, 200)

    def test_staff_user_sees_embedded_email_settings_section(self):
        user = User.objects.create_user(
            username="staffsettingsuser", password="x", email="staff@s.com", is_staff=True,
        )
        give_organization(user, "Staff Org")
        self.client.force_login(user)
        response = self.client.get(reverse("account:settings"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email settings")
        self.assertContains(response, 'id="email-settings-form"')

    def test_non_staff_user_does_not_see_email_settings_section(self):
        user = User.objects.create_user(username="plainuser", password="x", email="plain@s.com")
        give_organization(user, "Plain Org")
        self.client.force_login(user)
        response = self.client.get(reverse("account:settings"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="email-settings-form"')


class EmailSettingsInAccountSettingsTests(TestCase):
    def setUp(self):
        self.url = reverse("account:settings")

    def _staff_user(self):
        user = User.objects.create_user(
            username="staffuser", password="strong-pass", email="staff@example.com", is_staff=True,
        )
        give_organization(user, "Staff Org")
        return user

    def _regular_user(self):
        user = User.objects.create_user(
            username="regularuser", password="strong-pass", email="regular@example.com",
        )
        give_organization(user, "Regular Org")
        return user

    def test_non_staff_user_cannot_post_email_settings(self):
        self.client.force_login(self._regular_user())
        response = self.client.post(self.url, {
            "is_enabled": "on", "host": "smtp.example.com", "port": "587",
            "default_from_email": "no-reply@example.com",
        })
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.post(self.url, {"host": "smtp.example.com"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account:login"), response.url)

    def test_staff_user_can_save_custom_smtp_configuration(self):
        self.client.force_login(self._staff_user())
        response = self.client.post(self.url, {
            "is_enabled": "on",
            "host": "smtp.example.com",
            "port": "587",
            "use_tls": "on",
            "host_user": "user@example.com",
            "host_password": "super-secret",
            "default_from_email": "no-reply@example.com",
        })

        self.assertRedirects(response, self.url)
        email_settings = EmailSettings.load()
        self.assertTrue(email_settings.is_enabled)
        self.assertEqual(email_settings.host, "smtp.example.com")
        self.assertEqual(email_settings.host_password, "super-secret")

    def test_blank_password_keeps_previously_saved_password(self):
        self.client.force_login(self._staff_user())
        email_settings = EmailSettings.load()
        email_settings.host_password = "already-saved"
        email_settings.save()

        self.client.post(self.url, {
            "is_enabled": "on",
            "host": "smtp.example.com",
            "port": "587",
            "use_tls": "on",
            "host_user": "user@example.com",
            "host_password": "",
            "default_from_email": "no-reply@example.com",
        })

        self.assertEqual(EmailSettings.load().host_password, "already-saved")

    def test_enabling_without_host_is_rejected(self):
        self.client.force_login(self._staff_user())
        response = self.client.post(self.url, {
            "is_enabled": "on",
            "host": "",
            "port": "587",
            "host_user": "",
            "host_password": "",
            "default_from_email": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["email_form"].errors)

    def test_tls_and_ssl_together_is_rejected(self):
        self.client.force_login(self._staff_user())
        response = self.client.post(self.url, {
            "is_enabled": "on",
            "host": "smtp.example.com",
            "port": "587",
            "use_tls": "on",
            "use_ssl": "on",
            "host_user": "",
            "host_password": "",
            "default_from_email": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["email_form"].errors)
