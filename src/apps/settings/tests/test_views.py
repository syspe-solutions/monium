from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.settings.models import EmailSettings


class EmailSettingsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("settings:email_settings")

    def _create_staff_user(self):
        return get_user_model().objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password="strong-pass",
            is_staff=True,
            is_superuser=True,
        )

    def _create_regular_user(self):
        return get_user_model().objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="strong-pass",
            is_staff=False,
            is_superuser=True,
        )

    def test_anonymous_user_is_forbidden(self):
        # Mesmo comportamento de apps.organizations.mixins: raise_exception=True
        # no mixin de autorização prevalece sobre o redirect do LoginRequiredMixin.
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_non_staff_user_is_forbidden(self):
        self.client.force_login(self._create_regular_user())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_view_the_form(self):
        self.client.force_login(self._create_staff_user())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "settings/email_settings.html")

    def test_staff_user_can_save_custom_smtp_configuration(self):
        self.client.force_login(self._create_staff_user())
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
        self.client.force_login(self._create_staff_user())
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
        self.client.force_login(self._create_staff_user())
        response = self.client.post(self.url, {
            "is_enabled": "on",
            "host": "",
            "port": "587",
            "host_user": "",
            "host_password": "",
            "default_from_email": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

    def test_enabling_without_default_from_email_is_rejected(self):
        self.client.force_login(self._create_staff_user())
        response = self.client.post(self.url, {
            "is_enabled": "on",
            "host": "smtp.example.com",
            "port": "587",
            "use_tls": "on",
            "host_user": "",
            "host_password": "",
            "default_from_email": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

    def test_tls_and_ssl_together_is_rejected(self):
        self.client.force_login(self._create_staff_user())
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
        self.assertTrue(response.context["form"].errors)
